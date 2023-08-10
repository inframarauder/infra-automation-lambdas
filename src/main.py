from utils import ec2


def handler(event, context):
    ec2.cleanup()


if __name__ == "__main__":
    handler(None, None)
