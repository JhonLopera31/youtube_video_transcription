from airflow.models.param import Param

PARAMS = {
    "video_ids": Param(
        default="",
        description="list of youtube videos ids",
        type=["null", "array"],
    ),
    "keywords": Param(
        default="",
        description="list of youtube videos ids",
        type=["null", "array"],
    ),
    "cloud": Param(
        default="gcp",
        description="cloud where the process will be executed",
        enum=["aws", "gcp"],
    ),
}
