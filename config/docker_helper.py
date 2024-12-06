import os


def is_docker_container() -> bool:
    return os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
