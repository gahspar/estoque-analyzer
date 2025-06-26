import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from estoque_analyzer import EstoqueAnalyzer

# Configuração da página
st.set_page_config(
    page_title="Análise de Estoque",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("📊 Análise de Estoque")
st.markdown("""
Esta aplicação analisa o estoque atual comparando com as saídas mensais para identificar produtos que precisam de reposição.
""")

# Sidebar com instruções
with st.sidebar:
    st.header("📋 Instruções")
    st.markdown("""
    1. **Planilha de Estoque Atual**: Deve conter as colunas:
       - Código do produto
       - Descrição
       - Unidade de medida
       - Quantidade em estoque
    
    2. **Planilha de Saídas Mensais**: Deve conter as colunas:
       - Código do produto
       - Descrição
       - Unidade de medida
       - Quantidade de saídas
    """)
    
    st.header("ℹ️ Sobre")
    st.markdown("""
    A aplicação calcula a média de saída mensal e estima o estoque restante para o próximo mês.
    
    **Status:**
    - 🟢 OK: Estoque suficiente
    - 🔴 Comprar: Necessita reposição
    """)

def main():
    # Upload das planilhas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Upload - Estoque Atual")
        estoque_file = st.file_uploader(
            "Selecione a planilha de estoque atual",
            type=['xlsx', 'xls'],
            key="estoque"
        )
    
    with col2:
        st.subheader("📁 Upload - Saídas Mensais")
        saidas_file = st.file_uploader(
            "Selecione a planilha de saídas mensais",
            type=['xlsx', 'xls'],
            key="saidas"
        )
    
    # Configuração manual (opcional)
    st.markdown("---")
    st.subheader("⚙️ Configuração Manual (opcional)")
    config_manual = {}
    with st.expander("Ajustar leitura manualmente se necessário"):
        st.write("Se a detecção automática não funcionar, ajuste aqui:")
        col3, col4 = st.columns(2)
        with col3:
            linha_inicio_estoque = st.number_input("Linha de início dos dados de estoque (0 = auto)", min_value=0, value=0)
            mapeamento_estoque = st.text_input("Mapeamento colunas estoque (ex: 0,codigo;1,descricao;2,unidade;14,estoque)", value="")
        with col4:
            linha_inicio_saidas = st.number_input("Linha de início dos dados de saídas (0 = auto)", min_value=0, value=0)
            mapeamento_saidas = st.text_input("Mapeamento colunas saídas (ex: 0,codigo;1,descricao;2,unidade;14,saida)", value="")
        if linha_inicio_estoque > 0:
            config_manual['linha_inicio_estoque'] = linha_inicio_estoque
        if linha_inicio_saidas > 0:
            config_manual['linha_inicio_saidas'] = linha_inicio_saidas
        if mapeamento_estoque:
            config_manual['mapeamento_estoque'] = parse_mapeamento(mapeamento_estoque)
        if mapeamento_saidas:
            config_manual['mapeamento_saidas'] = parse_mapeamento(mapeamento_saidas)
    
    # Botão de análise
    if st.button("🔍 Analisar Estoque", type="primary", use_container_width=True):
        if estoque_file is None or saidas_file is None:
            st.error("❌ Por favor, faça upload de ambas as planilhas para continuar.")
            return
        
        try:
            with st.spinner("Analisando dados..."):
                analyzer = EstoqueAnalyzer()
                resultado = analyzer.analisar_estoque(estoque_file, saidas_file, config_manual if config_manual else None)
                if resultado is None:
                    st.error("❌ Erro ao processar os arquivos. Verifique se as colunas estão corretas ou ajuste manualmente.")
                    return
                
                # Salvar resultado na sessão
                st.session_state['resultado'] = resultado
                st.session_state['analise_feita'] = True
                
        except Exception as e:
            st.error(f"❌ Erro durante a análise: {str(e)}")
            st.exception(e)
    
    # Mostrar resultados se já foram calculados (apenas uma vez)
    if 'analise_feita' in st.session_state and st.session_state['analise_feita']:
        exibir_resultados(st.session_state['resultado'])

def parse_mapeamento(texto):
    # Exemplo: "0,codigo;1,descricao;2,unidade;14,estoque"
    mapeamento = {}
    for item in texto.split(';'):
        if ',' in item:
            idx, chave = item.split(',')
            mapeamento[chave.strip()] = int(idx.strip())
    return mapeamento

def exibir_resultados(resultado):
    """Exibe os resultados da análise de estoque"""
    
    # Estatísticas gerais
    total_produtos = len(resultado)
    produtos_ok = len(resultado[resultado['Situação'] == 'OK'])
    produtos_comprar = len(resultado[resultado['Situação'] == 'Comprar'])
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Produtos", total_produtos)
    
    with col2:
        st.metric("Status OK", produtos_ok, delta=f"{produtos_ok/total_produtos*100:.1f}%")
    
    with col3:
        st.metric("Precisa Comprar", produtos_comprar, delta=f"{produtos_comprar/total_produtos*100:.1f}%")
    
    with col4:
        valor_total_estoque = resultado['Quantidade em estoque'].sum()
        st.metric("Valor Total Estoque", f"{valor_total_estoque:,.0f}")
    
    st.divider()
    
    # Tabela de resultados
    st.subheader("📋 Resultado da Análise")
    
    # Aplicar formatação condicional
    def color_situacao(val):
        if val == 'Comprar':
            return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
        return 'background-color: #ccffcc; color: #006600; font-weight: bold'
    
    # Formatar números
    resultado_formatado = resultado.copy()
    resultado_formatado['Quantidade em estoque'] = resultado_formatado['Quantidade em estoque'].apply(lambda x: f"{x:,.0f}")
    resultado_formatado['Média de Saída Mensal'] = resultado_formatado['Média de Saída Mensal'].apply(lambda x: f"{x:,.2f}")
    resultado_formatado['Estoque Restante Estimado'] = resultado_formatado['Estoque Restante Estimado'].apply(lambda x: f"{x:,.2f}")
    
    # Exibir tabela com formatação (corrigido o warning)
    st.dataframe(
        resultado_formatado.style.map(color_situacao, subset=['Situação']),
        use_container_width=True,
        hide_index=True
    )
    
    # Botão de exportação (fora da função para evitar recarregamento)
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📥 Exportar para Excel", type="secondary", key="exportar_btn"):
            exportar_excel(resultado)
    
    with col2:
        st.info("💡 Dica: Clique em 'Exportar para Excel' para baixar os resultados da análise.")

def exportar_excel(resultado):
    """Exporta os resultados para um arquivo Excel"""
    try:
        # Mostrar spinner durante a exportação
        with st.spinner("Gerando arquivo Excel..."):
            # Criar nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analise_estoque_{timestamp}.xlsx"
            
            # Salvar arquivo temporário
            resultado.to_excel(filename, sheet_name='Análise de Estoque', index=False, engine='openpyxl')
            
            # Ler o arquivo e preparar para download
            with open(filename, 'rb') as f:
                file_content = f.read()
            
            # Limpar arquivo temporário
            import os
            if os.path.exists(filename):
                os.remove(filename)
            
            # Download
            st.download_button(
                label="💾 Baixar arquivo Excel",
                data=file_content,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_{timestamp}"
            )
            
            st.success(f"✅ Arquivo '{filename}' gerado com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro ao exportar arquivo: {str(e)}")
        st.exception(e)  # Mostrar detalhes do erro para debug

if __name__ == "__main__":
    main() 