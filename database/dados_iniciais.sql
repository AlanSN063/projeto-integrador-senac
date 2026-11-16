-- Categorias iniciais para permitir o cadastro de produtos.
INSERT INTO categoria_produto (nome, descricao) VALUES
    ('Peças Automotivas', 'Peças para manutenção de veículos'),
    ('Acessórios', 'Acessórios automotivos'),
    ('Produtos Químicos', 'Óleos, fluidos e produtos químicos'),
    ('Outros', 'Demais produtos')
ON CONFLICT (nome) DO NOTHING;