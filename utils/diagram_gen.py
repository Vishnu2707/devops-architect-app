from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.aws.storage import S3
from PIL import Image
import os

def generate_architecture_diagram(text):
    output_file = "utils/generated_architecture"
    try:
        with Diagram("Web App Infra on AWS", filename=output_file, show=False):
            with Cluster("VPC"):
                elb = ELB("ALB")
                frontend = S3("React App")
                backend = EC2("Node.js App")
                db = RDS("PostgreSQL")

                frontend >> elb >> backend >> db
        return output_file + ".png" if os.path.exists(output_file + ".png") else None
    except:
        return None

