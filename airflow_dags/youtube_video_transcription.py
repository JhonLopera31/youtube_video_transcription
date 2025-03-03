import logging
from datetime import datetime

from airflow.decorators import dag, task, task_group
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.operators.batch import BatchOperator
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.trigger_rule import TriggerRule
from youtube_transcription.configs import configs
from youtube_transcription.input_params import PARAMS
from youtube_transcription.queries import GET_VIDEOS_BY_KEYWORD, GET_VIDEOS_EXISTENCE

ENV = Variable.get("env")
logger = logging.getLogger(__name__)


dag_parameters = {
    "dag_id": "youtube_video_transcription",
    "start_date": datetime(2025, 2, 1),
    "schedule_interval": None,
    "default_args": {"owner": "Jhon Lopera | test", "retries": 0},
    "catchup": False,
    "tags": ["transcription"],
    "max_active_tasks": 64,  # control the amount of containers executed
    "params": PARAMS,
}


@task
def check_if_video_id_exist(**context):
    video_ids = context.get("params").get("video_ids")
    hook = PostgresHook(postgres_conn_id=configs.POSTGRES_CONN_ID.get(ENV))
    query = GET_VIDEOS_EXISTENCE.format(video_ids=str(video_ids).replace("[", "").replace("]", ""))
    logger.info(query)
    result = hook.get_records(query)
    return [x[0] for x in result]


@task
def get_transcription_execution_arguments(**context):
    video_ids = context.get("ti").xcom_pull(task_ids="check_if_video_id_exist")
    overrides_list = []

    for video_id in video_ids:
        if context.get("params").get("cloud") == "gcp":
            override = {"container_overrides": [{"args": ["--video_id", video_id]}]}
        else:
            command = f"python main.py --video_id {video_id}"
            override = {"command": command.split(" "), "resourceRequirements": configs.AWS_BATCH_RESOURCES.get(ENV)}
        overrides_list.append(override)

    return overrides_list


@task_group()
def execute_transcription_gcp():
    get_execution_arguments_gcp_task = get_transcription_execution_arguments()
    execute_cloud_run_job = CloudRunExecuteJobOperator.partial(
        task_id="execute_transcription_gcp",
        job_name="transcription_process_worker",
        project_id=configs.GCP_PROJECT_IDS.get(ENV),
        gcp_conn_id=configs.GCP_CONNECTION_IDS.get(ENV),
        region=configs.GCP_REGION.get(ENV),
        pool="transcription_process_pool_gcp",  ## control de amount of jobs in gcp
        deferrable=True,
    ).expand(overrides=get_execution_arguments_gcp_task)

    get_execution_arguments_gcp_task >> execute_cloud_run_job


@task_group()
def execute_transcription_aws():
    get_execution_arguments_task = get_transcription_execution_arguments()
    aws_batch = BatchOperator.partial(
        aws_conn_id=configs.AWS_CONNECTION_IDS.get(ENV),
        task_id="transcription_process",
        job_name="transcription_process",
        job_queue=configs.BATCH_JOB_QUEUE_NAME.get(ENV),
        job_definition=configs.BATCH_JOB_DEFINITION.get(ENV),
        region_name=configs.AWS_REGION.get(ENV),
        pool="transcription_process_pool_aws",  ## control de amount of jobs in aws
        deferrable=True,
    ).expand(overrides=get_execution_arguments_task)

    get_execution_arguments_task >> aws_batch


@task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
def get_related_videos(**context):
    video_ids = context.get("params").get("keywords")
    if not video_ids:
        logger.info("No keywords provided")
        return
    logger.info(video_ids)
    hook = PostgresHook(postgres_conn_id=configs.POSTGRES_CONN_ID.get(ENV))
    query = GET_VIDEOS_BY_KEYWORD.format(keywords="|".join(video_ids))

    logger.info(f"query: {query}")
    results = hook.get_records(query)
    return results


@task.branch()
def cloud_selection_branch(**context):
    video_ids = context.get("ti").xcom_pull(task_ids="check_if_video_id_exist")
    if context.get("params").get("cloud") == "gcp" and video_ids:
        return "execute_transcription_gcp.get_transcription_execution_arguments"
    elif context.get("params").get("cloud") == "aws" and video_ids:
        return "execute_transcription_aws.get_transcription_execution_arguments"
    return "get_related_videos"


@dag(**dag_parameters)
def dag():
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")
    check_if_video_id_exist_task = check_if_video_id_exist()
    branch = cloud_selection_branch()
    execute_transcription_aws_task = execute_transcription_aws()
    execute_transcription_gcp_task = execute_transcription_gcp()
    get_video_ids = get_related_videos()

    start >> check_if_video_id_exist_task >> branch
    branch >> [execute_transcription_aws_task, execute_transcription_gcp_task] >> get_video_ids >> end


dag()
