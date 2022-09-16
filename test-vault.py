import hvac

client = hvac.Client(
    url='http://127.0.0.1:8200',
    token='dev-only-token',
)

create_response = client.secrets.kv.v2.create_or_update_secret(
    path='my-secret-password',
    secret=dict(password='Hashi123'),
)

print('Secret written successfully.')

read_response = client.secrets.kv.read_secret_version(path='my-secret-password')
password = read_response['data']['data']['password']
print(password)
