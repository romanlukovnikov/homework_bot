import hvac


client = hvac.Client(url='http://51.250.68.170:8200')

shares = 5
threshold = 3
result = client.sys.initialize(shares, threshold)
root_token = result['root_token']
keys = result['keys']
print(f'Инициализирован: {client.sys.is_initialized()}')
print(client.sys.is_sealed())
"""
client.sys.submit_unseal_keys(keys)
print(client.sys.read_seal_status())
# client.sys.seal()
# client.sys.unseal_multi(unseal_keys)
client.token = root_token
assert client.is_authenticated()

#client.kv.default_kv_version = 1
#create_response = client.secrets.kv.v1.create_or_update_secret('foo', secret=dict(baz='bar'))
print(root_token)
print(keys)

client.sys.enable_secrets_engine(
    backend_type='kv',
    path='secret',
)

init_secrets = {
    'TELEGRAM_TOKEN': '',
    'PRACTICUM_TOKEN': '',
    'TELEGRAM_CHAT_ID': '',
}

client.secrets.kv.v1.create_or_update_secret(
    path='chat-bot',
    secret=init_secrets,
)




create_response = client.secrets.kv.v2.create_or_update_secret(
    path='my-secret-password',
    secret=dict(password='Hashi123'),
)

print('Secret written successfully.')

read_response = client.secrets.kv.read_secret_version(path='my-secret-password')
password = read_response['data']['data']['password']
print(password)
"""