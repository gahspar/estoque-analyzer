# 📊 Sistema de Análise de Estoque

## 📋 Descrição do Projeto

Sistema web desenvolvido em Python para análise inteligente de estoque, que compara dados de estoque atual com saídas mensais para identificar produtos que necessitam de reposição. A aplicação calcula automaticamente a média de saída mensal, estima o estoque restante e fornece recomendações de compra.

## 🚀 Funcionalidades Principais

### ✅ Análise Automática
- **Upload de Planilhas**: Suporte para arquivos Excel (.xlsx, .xls)
- **Detecção Inteligente**: Identificação automática de cabeçalhos e estrutura de dados
- **Mapeamento Flexível**: Configuração manual de colunas quando necessário
- **Processamento Robusto**: Tratamento de diferentes formatos de planilhas

### 📈 Cálculos e Métricas
- **Média de Saída Mensal**: Cálculo baseado em dados históricos
- **Estoque Restante Estimado**: Projeção para o próximo período
- **Status de Reposição**: Classificação automática (OK/Comprar)
- **Estatísticas Gerais**: Total de produtos, percentuais e valores

### 🎨 Interface Moderna
- **Design Responsivo**: Interface adaptável para diferentes dispositivos
- **Formatação Visual**: Destaque em vermelho para itens que precisam de compra
- **Métricas Visuais**: Cards com estatísticas em tempo real
- **Exportação**: Download dos resultados em formato Excel

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**: Linguagem principal
- **Pandas**: Manipulação e análise de dados
- **OpenPyXL**: Leitura e escrita de arquivos Excel
- **NumPy**: Cálculos numéricos

### Frontend
- **Streamlit**: Framework web para interface
- **CSS Customizado**: Formatação condicional das tabelas

### Desenvolvimento
- **Logging**: Sistema de logs para debug
- **Tratamento de Erros**: Gestão robusta de exceções
- **Sessões**: Persistência de dados entre interações

## 📁 Estrutura do Projeto

```
Estoque/
├── app.py                 # Interface principal (Streamlit)
├── estoque_analyzer.py    # Lógica de análise de dados
├── requirements.txt       # Dependências do projeto
├── README.md             # Documentação (este arquivo)
├── run.py                # Script de execução alternativo
├── debug_planilhas.py    # Script para debug de planilhas
├── analisar_planilhas.py # Script de análise standalone
├── exemplos/
│   └── estoque_exemplo.py # Exemplos de uso
├── Saídas de Insumos.xlsx # Planilha de exemplo (saídas)
└── Saldos de Estoque.xlsx # Planilha de exemplo (estoque)
```

## 🔧 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd Estoque
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv .venv
   ```

3. **Ative o ambiente virtual**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute a aplicação**
   ```bash
   streamlit run app.py
   ```

## 📖 Como Usar

### 1. Preparação das Planilhas

#### Planilha de Estoque Atual
Deve conter as seguintes informações:
- **Código do produto**: Identificador único
- **Descrição**: Nome/descrição do produto
- **Unidade de medida**: Unidade (kg, un, l, etc.)
- **Quantidade em estoque**: Quantidade atual disponível

#### Planilha de Saídas Mensais
Deve conter as seguintes informações:
- **Código do produto**: Mesmo identificador da planilha de estoque
- **Descrição**: Nome/descrição do produto
- **Unidade de medida**: Unidade (kg, un, l, etc.)
- **Quantidade de saídas**: Quantidade vendida/consumida no período

### 2. Processo de Análise

1. **Upload das Planilhas**
   - Faça upload da planilha de estoque atual
   - Faça upload da planilha de saídas mensais

2. **Configuração (Opcional)**
   - Se a detecção automática não funcionar, use a configuração manual
   - Especifique a linha de início dos dados
   - Mapeie as colunas manualmente se necessário

3. **Execução da Análise**
   - Clique em "Analisar Estoque"
   - Aguarde o processamento dos dados

4. **Visualização dos Resultados**
   - Analise as métricas gerais
   - Visualize a tabela com os resultados
   - Identifique produtos que precisam de reposição (destacados em vermelho)

5. **Exportação**
   - Clique em "Exportar para Excel" para baixar os resultados

## 🔍 Funcionalidades Avançadas

### Detecção Automática
O sistema utiliza algoritmos inteligentes para:
- Identificar automaticamente a linha de início dos dados
- Mapear colunas por heurística baseada em conteúdo
- Tratar diferentes formatos de planilhas

### Configuração Manual
Quando a detecção automática falha, você pode:
- Especificar manualmente a linha de início dos dados
- Mapear colunas usando índices (ex: 0,codigo;1,descricao;14,estoque)
- Ajustar configurações específicas para cada planilha

### Tratamento de Erros
O sistema inclui:
- Validação de arquivos de entrada
- Tratamento de dados ausentes ou inválidos
- Logs detalhados para debug
- Mensagens de erro informativas

## 📊 Exemplo de Saída

### Métricas Gerais
- **Total de Produtos**: 206
- **Status OK**: 180 (87.4%)
- **Precisa Comprar**: 26 (12.6%)
- **Valor Total Estoque**: 1,234,567

### Tabela de Resultados
| Código | Descrição | Unidade | Estoque Atual | Média Mensal | Estoque Estimado | Situação |
|--------|-----------|---------|---------------|--------------|------------------|----------|
| 001 | Produto A | kg | 1,000 | 150.5 | 849.5 | OK |
| 002 | Produto B | un | 50 | 75.2 | -25.2 | 🔴 Comprar |

## 🐛 Solução de Problemas

### Problemas Comuns

1. **Erro de Upload**
   - Verifique se os arquivos são Excel (.xlsx ou .xls)
   - Confirme se as planilhas contêm os dados necessários

2. **Detecção Automática Falha**
   - Use a configuração manual
   - Verifique a estrutura das planilhas
   - Consulte os logs para mais detalhes

3. **Dados Não Correspondem**
   - Verifique se os códigos dos produtos são idênticos
   - Confirme se as unidades de medida estão corretas

### Logs e Debug
- Os logs são exibidos no terminal durante a execução
- Use `debug_planilhas.py` para analisar a estrutura das planilhas
- Verifique o console do navegador para erros de interface

## 🔄 Versões e Atualizações

### Versão 1.0.0 (Atual)
- ✅ Interface web completa com Streamlit
- ✅ Detecção automática de dados
- ✅ Configuração manual de colunas
- ✅ Exportação para Excel
- ✅ Formatação condicional
- ✅ Tratamento robusto de erros
- ✅ Sistema de logs
- ✅ Persistência de sessão

### Próximas Funcionalidades
- 📊 Gráficos e visualizações
- 📈 Histórico de análises
- 🔔 Alertas automáticos
- 📱 Interface mobile otimizada
- 🔗 Integração com sistemas ERP

## 👥 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas, sugestões ou problemas:
- Abra uma issue no GitHub
- Entre em contato através do email: [seu-email@exemplo.com]

## 🙏 Agradecimentos

- Comunidade Streamlit pelo framework incrível
- Pandas pela biblioteca de análise de dados
- Todos os contribuidores e testadores

---

**Desenvolvido com ❤️ para otimizar a gestão de estoque** 