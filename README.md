# sitema de contole de estoque

As telas planejadas são:
1. Login: acesso com usuário e senha.
2. Dashboard: resumo de produtos, fornecedores, ordens de serviço e movimentações.
3. Cadastro de produtos: nome, categoria, fornecedor, código, preço e estoque mínimo.
4. Ordens de serviço: controle de clientes, veículos e situação dos serviços.

2. Identidade visual
Paleta de cores

Azul-marinho#102D50
Azul#1769D2
Cinza claro#F4F7FB
Branco#FFFFFF


Tipografia
- Títulos: Poppins SemiBold.
- Subtítulos: Poppins Medium.
- Textos e campos: Roboto Regular.
- Botões: Roboto Medium.

3. Organização do sistema
Menu	Funcionalidade
Início	Dashboard
Produtos	Cadastro e consulta
Fornecedores	Cadastro e consulta
Categorias	Organização de produtos
Ordens de serviço	Controle de serviços
Movimentações	Entradas e saídas
Usuários	Controle de acesso
Relatórios	Indicadores e consultas
Configurações	Ajustes do sistema

## Integração dos Controllers e PostgreSQL

1. Instale as dependências: `pip install -r requirements.txt`.
2. Configure as variáveis `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD` (os padrões atuais são localhost, 5432, projetoi, postgres e 123456).
3. No pgAdmin, abra o banco `projetoi` e execute `database/migracao_senha_usuario.sql` e depois `database/dados_iniciais.sql`.
4. No terminal, execute `python criar_usuario.py` para criar o primeiro usuário administrador com senha protegida por hash.
5. Inicie com `python app.py`.

As telas integradas nesta etapa são Login, Dashboard, Produtos e Ordens de Serviço. Fornecedores, Categorias, Movimentações, Usuários e Relatórios ainda usam telas de placeholder e serão integradas quando suas Views forem implementadas.

Observação: o estoque atual é calculado pelas movimentações registradas em `movimentacao_estoque` e `item_movimentacao`. O cadastro de produto não cria saldo inicial automaticamente.
