import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from estoque_analyzer import EstoqueAnalyzer
from analise_avancada import AnaliseAvancada

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Análise de Estoque",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("📊 Dashboard de Análise de Estoque Avançada")
st.markdown("""
Sistema inteligente para análise de estoque com previsão de demanda, análise sazonal e sugestões de compra.
Especialmente otimizado para **medicamentos em unidades de saúde**.
""")

# Sidebar com configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Seleção de tipo de produto
    tipo_produto = st.selectbox(
        "Tipo de Produto",
        ["medicamentos", "insumos", "equipamentos"],
        help="Selecione o tipo de produto para aplicar fatores de correção específicos"
    )
    
    # Média de pacientes (para medicamentos)
    if tipo_produto == "medicamentos":
        media_pacientes = st.number_input(
            "Média Mensal de Pacientes",
            min_value=0,
            value=1000,
            help="Média mensal de pacientes para cálculo de demanda esperada"
        )
    else:
        media_pacientes = None
    
    st.divider()
    
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
    **Funcionalidades Avançadas:**
    - 🎯 Previsão de demanda baseada em pacientes
    - 📈 Análise sazonal automática
    - 💡 Sugestões inteligentes de compra
    - 📊 Dashboard com visualizações
    - 🔔 Alertas e recomendações
    
    **Status:**
    - 🟢 OK: Estoque suficiente
    - 🔴 Comprar: Necessita reposição
    """)

def criar_metricas_principais(resultado):
    """Cria métricas principais do dashboard"""
    if resultado is None or len(resultado) == 0:
        return
    
    # Calcular métricas
    total_produtos = len(resultado)
    produtos_ok = len(resultado[resultado['Situação'] == 'OK'])
    produtos_comprar = len(resultado[resultado['Situação'] == 'Comprar'])
    valor_total_estoque = resultado['Quantidade em estoque'].sum()
    
    # Métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Produtos", 
            total_produtos,
            help="Número total de produtos analisados"
        )
    
    with col2:
        st.metric(
            "Status OK", 
            produtos_ok, 
            delta=f"{produtos_ok/total_produtos*100:.1f}%",
            delta_color="normal",
            help="Produtos com estoque suficiente"
        )
    
    with col3:
        st.metric(
            "Precisa Comprar", 
            produtos_comprar, 
            delta=f"{produtos_comprar/total_produtos*100:.1f}%",
            delta_color="inverse",
            help="Produtos que precisam de reposição"
        )
    
    with col4:
        st.metric(
            "Valor Total Estoque", 
            f"{valor_total_estoque:,.0f}",
            help="Soma total de todas as quantidades em estoque"
        )

def criar_grafico_pizza(resultado):
    """Cria gráfico de pizza com distribuição de situação"""
    if resultado is None or len(resultado) == 0:
        return
    
    # Preparar dados
    situacoes = resultado['Situação'].value_counts()
    
    # Cores
    cores = {'OK': '#00ff88', 'Comprar': '#ff4444'}
    
    # Criar gráfico
    fig = px.pie(
        values=situacoes.values,
        names=situacoes.index,
        title="Distribuição por Situação",
        color_discrete_map=cores
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def criar_grafico_barras_top_produtos(resultado, top_n=10):
    """Cria gráfico de barras com top produtos"""
    if resultado is None or len(resultado) == 0:
        return
    
    # Top produtos por saída mensal
    top_saidas = resultado.nlargest(top_n, 'Média de Saída Mensal')
    
    fig = px.bar(
        top_saidas,
        x='Descrição',
        y='Média de Saída Mensal',
        title=f"Top {top_n} Produtos por Saída Mensal",
        color='Situação',
        color_discrete_map={'OK': '#00ff88', 'Comprar': '#ff4444'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def criar_grafico_estoque_vs_demanda(resultado):
    """Cria gráfico de dispersão estoque vs demanda"""
    if resultado is None or len(resultado) == 0:
        return
    
    fig = px.scatter(
        resultado,
        x='Média de Saída Mensal',
        y='Quantidade em estoque',
        color='Situação',
        size='Demanda Esperada',
        hover_data=['Descrição', 'Prazo Estoque (dias)'],
        title="Estoque vs Demanda Mensal",
        color_discrete_map={'OK': '#00ff88', 'Comprar': '#ff4444'}
    )
    
    # Adicionar linha de equilíbrio
    max_val = max(resultado['Média de Saída Mensal'].max(), resultado['Quantidade em estoque'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Linha de Equilíbrio',
            line=dict(color='gray', dash='dash')
        )
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def criar_grafico_prazo_estoque(resultado):
    """Cria gráfico de prazo de estoque"""
    if resultado is None or len(resultado) == 0:
        return
    
    # Categorizar por prazo
    def categorizar_prazo(prazo):
        if prazo < 0:
            return 'Crítico (< 0 dias)'
        elif prazo < 30:
            return 'Baixo (0-30 dias)'
        elif prazo < 90:
            return 'Normal (30-90 dias)'
        else:
            return 'Alto (> 90 dias)'
    
    resultado['Categoria Prazo'] = resultado['Prazo Estoque (dias)'].apply(categorizar_prazo)
    
    # Contar por categoria
    categorias = resultado['Categoria Prazo'].value_counts()
    
    fig = px.bar(
        x=categorias.index,
        y=categorias.values,
        title="Distribuição por Prazo de Estoque",
        color=categorias.index,
        color_discrete_map={
            'Crítico (< 0 dias)': '#ff0000',
            'Baixo (0-30 dias)': '#ffaa00',
            'Normal (30-90 dias)': '#00ff88',
            'Alto (> 90 dias)': '#0088ff'
        }
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def exibir_recomendacoes(resultado):
    """Exibe recomendações baseadas na análise"""
    if resultado is None or len(resultado) == 0:
        return
    
    analise = AnaliseAvancada()
    recomendacoes = analise.gerar_recomendacoes(resultado)
    
    st.subheader("💡 Recomendações Inteligentes")
    
    for rec in recomendacoes:
        with st.expander(f"🔔 {rec['titulo']}"):
            st.write(rec['descricao'])
            
            if rec['produtos']:
                df_rec = pd.DataFrame(rec['produtos'])
                st.dataframe(df_rec, use_container_width=True, hide_index=True)

def exibir_tabela_resultados(resultado):
    """Exibe tabela de resultados com formatação"""
    if resultado is None or len(resultado) == 0:
        return
    
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
    resultado_formatado['Demanda Esperada'] = resultado_formatado['Demanda Esperada'].apply(lambda x: f"{x:,.2f}")
    resultado_formatado['Estoque Restante Estimado'] = resultado_formatado['Estoque Restante Estimado'].apply(lambda x: f"{x:,.2f}")
    resultado_formatado['Prazo Estoque (dias)'] = resultado_formatado['Prazo Estoque (dias)'].apply(lambda x: f"{x:,.1f}")
    resultado_formatado['Quantidade Sugerida Compra'] = resultado_formatado['Quantidade Sugerida Compra'].apply(lambda x: f"{x:,.2f}")
    
    # Exibir tabela com formatação
    st.dataframe(
        resultado_formatado.style.map(color_situacao, subset=['Situação']),
        use_container_width=True,
        hide_index=True
    )

def exportar_excel(resultado):
    """Exporta os resultados para um arquivo Excel"""
    try:
        with st.spinner("Gerando arquivo Excel..."):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analise_estoque_avancada_{timestamp}.xlsx"
            
            # Salvar arquivo temporário
            resultado.to_excel(filename, sheet_name='Análise Avançada', index=False, engine='openpyxl')
            
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
            with st.spinner("Analisando dados com análise avançada..."):
                analyzer = EstoqueAnalyzer()
                resultado = analyzer.analisar_estoque(
                    estoque_file, 
                    saidas_file, 
                    config_manual if config_manual else None,
                    tipo_produto,
                    media_pacientes
                )
                
                if resultado is None:
                    st.error("❌ Erro ao processar os arquivos. Verifique se as colunas estão corretas ou ajuste manualmente.")
                    return
                
                # Salvar resultado na sessão
                st.session_state['resultado'] = resultado
                st.session_state['analise_feita'] = True
                st.session_state['tipo_produto'] = tipo_produto
                st.session_state['media_pacientes'] = media_pacientes
                
        except Exception as e:
            st.error(f"❌ Erro durante a análise: {str(e)}")
            st.exception(e)
    
    # Mostrar resultados se já foram calculados
    if 'analise_feita' in st.session_state and st.session_state['analise_feita']:
        resultado = st.session_state['resultado']
        
        # Informações da análise
        st.markdown("---")
        st.subheader("📊 Dashboard de Resultados")
        
        # Informações do tipo de produto
        if st.session_state.get('tipo_produto'):
            st.info(f"🎯 **Tipo de Produto:** {st.session_state['tipo_produto'].title()}")
        if st.session_state.get('media_pacientes'):
            st.info(f"👥 **Média de Pacientes:** {st.session_state['media_pacientes']:,} pacientes/mês")
        
        # Métricas principais
        criar_metricas_principais(resultado)
        
        # Gráficos
        st.markdown("---")
        st.subheader("📈 Visualizações")
        
        # Primeira linha de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            criar_grafico_pizza(resultado)
        
        with col2:
            criar_grafico_prazo_estoque(resultado)
        
        # Segunda linha de gráficos
        col3, col4 = st.columns(2)
        
        with col3:
            criar_grafico_barras_top_produtos(resultado)
        
        with col4:
            criar_grafico_estoque_vs_demanda(resultado)
        
        # Recomendações
        st.markdown("---")
        exibir_recomendacoes(resultado)
        
        # Tabela de resultados
        st.markdown("---")
        exibir_tabela_resultados(resultado)
        
        # Botão de exportação
        st.divider()
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("📥 Exportar para Excel", type="secondary", key="exportar_btn"):
                exportar_excel(resultado)
        
        with col2:
            st.info("💡 Dica: Clique em 'Exportar para Excel' para baixar os resultados da análise avançada.")

def parse_mapeamento(texto):
    """Parse do mapeamento manual de colunas"""
    mapeamento = {}
    for item in texto.split(';'):
        if ',' in item:
            idx, chave = item.split(',')
            mapeamento[chave.strip()] = int(idx.strip())
    return mapeamento

if __name__ == "__main__":
    main() 