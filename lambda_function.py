import json
import boto3
import base64
import psycopg2
from botocore.exceptions import ClientError

class Product:
  def __init__(self, id, name, desc):
    self.id = id
    self.name = name
    self.desc = desc
    
def get_secret():
  secret_name = 'python_rds_secret'
  region_name = 'us-east-2'
  
  session = boto3.session.Session()
  client = session.client(service_name='secretsmanager', region_name=region_name)
  
  try:
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
  except ClientError as e:
    raise e
  else:
    if 'SecretString' in get_secret_value_response:
      secret = get_secret_value_response['SecretString']
    else:
      secret = base64.b64decode(get_secret_value_response['SecretBinary'])
  
  return secret


def get_connection():
  secret = get_secret()
  return psycopg2.connect(
    host=json.loads(secret)['db_endpoint_pg'],
    database='postgres',
    user=json.loads(secret)['db_user'],
    password=json.loads(secret)['db_pass']
  )

def lambda_handler(event, context):
  con = None
  try:
    con = get_connection()
    cur = con.cursor()
    cur.execute(FETCH_QUERY)
    
    products = []
    row = cur.fetchone()
    
    while row is not None:
      product = Product(row[0], row[1], row[2])
      products.append(product.__dict__)
      row = cur.fetchone()
    
    res = json.dumps(products)
    print(res)
    return {
      'statusCode': 200,
      'body': res
    }
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    raise error
  finally:
    if con is not None:
      con.close()

  

    
  
  

