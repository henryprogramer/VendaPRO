# Modo de operação
MODE = "offline"  # "online" ou "offline"

# Configurações do banco
DB_CONFIG = {
    "NAME": "vendapro",
    "USER": "venda_user",
    "PASSWORD": "venda_pass",
    "HOST": "localhost" if MODE=="offline" else "IP_DO_SERVIDOR",
    "PORT": 5432
}
