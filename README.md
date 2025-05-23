# 🎫 Ticket System with Microservices

## 📖 Descrição

Este projeto utiliza **Docker Compose** para orquestração de múltiplos serviços em contêineres. A seguir estão todas as instruções e informações necessárias para executar e gerenciar o ambiente de forma prática e eficiente.

---

## 📦 Tecnologias Utilizadas

- **Docker**: Contêinerização de serviços.
- **Docker Compose**: Orquestração dos contêineres.
- **FastAPI** (caso aplicável).
- **SQLite** (caso aplicável).


---

## 🏗️ Instalação

1. Clone este repositório:
    ```sh
    git clone https://github.com/seu-usuario/projeto-docker-compose.git
    cd projeto-docker-compose
    ```


3. Inicie os serviços normalmente:
    ```sh
    docker compose up --build
    ```

4. Caso queira rodar os serviços em segundo plano (modo _detached_):
    ```sh
    docker compose up --build -d
    ```

---

## 🌐 Portas dos Serviços

Os serviços estão configurados para rodar nas seguintes portas locais:

| Serviço    | Porta | URL de Acesso           |
|------------|------|------------------------|
| Serviços de autenticação | 8001 | [http://localhost:8001](http://localhost:8001) |
| Serviços de usuário   | 8002 | [http://localhost:8002](http://localhost:8002) |
| Serviço de ingressos  | 8003 | [http://localhost:8003](http://localhost:8003) |

Certifique-se de que essas portas estão disponíveis para evitar conflitos.

---

## 🛑 Como parar os serviços

Para interromper todos os containers e liberar os recursos utilizados:

```sh
docker compose down
