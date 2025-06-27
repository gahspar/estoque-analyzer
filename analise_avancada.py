import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class AnaliseAvancada:
    """Classe para análise avançada de estoque com previsão de demanda"""
    
    def __init__(self):
        self.modelo_demanda = None
        self.scaler = StandardScaler()
        self.tipo_produto = None
        self.media_pacientes = None
        
    def configurar_tipo_produto(self, tipo_produto, media_pacientes=None):
        """Configura o tipo de produto e média de pacientes"""
        self.tipo_produto = tipo_produto
        self.media_pacientes = media_pacientes
        
        # Fatores de correlação por tipo de produto
        self.fatores_correcao = {
            'medicamentos': {
                'fator_paciente': 0.8,  # 80% dos pacientes usam medicamentos
                'fator_sazonal': 1.2,   # 20% de variação sazonal
                'estoque_minimo': 0.3,  # 30% do estoque como mínimo
                'prazo_seguranca': 15   # 15 dias de segurança
            },
            'insumos': {
                'fator_paciente': 0.6,
                'fator_sazonal': 1.1,
                'estoque_minimo': 0.2,
                'prazo_seguranca': 10
            },
            'equipamentos': {
                'fator_paciente': 0.4,
                'fator_sazonal': 1.0,
                'estoque_minimo': 0.5,
                'prazo_seguranca': 30
            }
        }
    
    def calcular_demanda_esperada(self, media_saida_mensal, media_pacientes=None):
        """Calcula a demanda esperada baseada na média de pacientes"""
        if media_pacientes is None:
            media_pacientes = self.media_pacientes
            
        if media_pacientes is None:
            return media_saida_mensal
            
        fatores = self.fatores_correcao.get(self.tipo_produto, self.fatores_correcao['medicamentos'])
        
        # Demanda baseada em pacientes
        demanda_pacientes = media_saida_mensal * (media_pacientes / 1000) * fatores['fator_paciente']
        
        # Aplicar fator sazonal
        demanda_ajustada = demanda_pacientes * fatores['fator_sazonal']
        
        return max(demanda_ajustada, media_saida_mensal * 0.5)  # Mínimo 50% da média histórica
    
    def prever_demanda_futura(self, dados_historicos, meses_futuros=3):
        """Prevê demanda futura usando machine learning"""
        if len(dados_historicos) < 3:
            return None
            
        # Preparar dados para ML
        X = np.arange(len(dados_historicos)).reshape(-1, 1)
        y = dados_historicos.values
        
        # Treinar modelo
        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X, y)
        
        # Prever próximos meses
        X_futuro = np.arange(len(dados_historicos), len(dados_historicos) + meses_futuros).reshape(-1, 1)
        previsoes = modelo.predict(X_futuro)
        
        return previsoes
    
    def calcular_prazo_estoque(self, estoque_atual, demanda_esperada):
        """Calcula quantos dias o estoque atual durará"""
        if demanda_esperada <= 0:
            return float('inf')
        
        # Converter demanda mensal para diária
        demanda_diaria = demanda_esperada / 30
        
        if demanda_diaria <= 0:
            return float('inf')
            
        prazo_dias = estoque_atual / demanda_diaria
        
        return prazo_dias
    
    def sugerir_quantidade_compra(self, estoque_atual, demanda_esperada, prazo_desejado=90):
        """Sugere quantidade ideal para compra"""
        fatores = self.fatores_correcao.get(self.tipo_produto, self.fatores_correcao['medicamentos'])
        
        # Estoque mínimo necessário
        estoque_minimo = estoque_atual * fatores['estoque_minimo']
        
        # Demanda para o período desejado
        demanda_periodo = demanda_esperada * (prazo_desejado / 30)
        
        # Estoque necessário
        estoque_necessario = estoque_minimo + demanda_periodo
        
        # Quantidade a comprar
        quantidade_comprar = max(0, estoque_necessario - estoque_atual)
        
        # Aplicar fator de segurança
        quantidade_comprar *= 1.1  # 10% de segurança
        
        return round(quantidade_comprar, 2)
    
    def analisar_sazonalidade(self, dados_mensais):
        """Analisa padrões sazonais nos dados"""
        if len(dados_mensais) < 12:
            return None
            
        # Calcular médias por mês
        dados_df = pd.DataFrame({
            'mes': range(1, len(dados_mensais) + 1),
            'demanda': dados_mensais
        })
        
        # Identificar padrões sazonais
        media_geral = dados_mensais.mean()
        variacao_sazonal = []
        
        for i in range(0, len(dados_mensais), 12):
            periodo = dados_mensais[i:i+12]
            if len(periodo) == 12:
                variacao = (periodo - media_geral) / media_geral
                variacao_sazonal.append(variacao)
        
        if variacao_sazonal:
            variacao_media = np.mean(variacao_sazonal, axis=0)
            return variacao_media
        
        return None
    
    def calcular_indicadores_avancados(self, resultado_analise):
        """Calcula indicadores avançados para o dashboard"""
        if resultado_analise is None or len(resultado_analise) == 0:
            return {}
        
        # Indicadores básicos
        total_produtos = len(resultado_analise)
        produtos_criticos = len(resultado_analise[resultado_analise['Situação'] == 'Comprar'])
        produtos_ok = len(resultado_analise[resultado_analise['Situação'] == 'OK'])
        
        # Valor total em estoque
        valor_total_estoque = resultado_analise['Quantidade em estoque'].sum()
        
        # Média de saída mensal
        media_saida_geral = resultado_analise['Média de Saída Mensal'].mean()
        
        # Produtos com estoque baixo (menos de 30 dias)
        produtos_estoque_baixo = len(resultado_analise[
            resultado_analise['Estoque Restante Estimado'] < 0
        ])
        
        # Produtos com estoque excessivo (mais de 180 dias)
        produtos_estoque_excessivo = len(resultado_analise[
            resultado_analise['Estoque Restante Estimado'] > 180
        ])
        
        # Categorização por urgência
        urgente = len(resultado_analise[
            resultado_analise['Estoque Restante Estimado'] < -30
        ])
        
        atencao = len(resultado_analise[
            (resultado_analise['Estoque Restante Estimado'] >= -30) & 
            (resultado_analise['Estoque Restante Estimado'] < 0)
        ])
        
        normal = len(resultado_analise[
            (resultado_analise['Estoque Restante Estimado'] >= 0) & 
            (resultado_analise['Estoque Restante Estimado'] <= 90)
        ])
        
        excessivo = len(resultado_analise[
            resultado_analise['Estoque Restante Estimado'] > 90
        ])
        
        return {
            'total_produtos': total_produtos,
            'produtos_criticos': produtos_criticos,
            'produtos_ok': produtos_ok,
            'valor_total_estoque': valor_total_estoque,
            'media_saida_geral': media_saida_geral,
            'produtos_estoque_baixo': produtos_estoque_baixo,
            'produtos_estoque_excessivo': produtos_estoque_excessivo,
            'categorias': {
                'urgente': urgente,
                'atencao': atencao,
                'normal': normal,
                'excessivo': excessivo
            },
            'percentual_critico': (produtos_criticos / total_produtos * 100) if total_produtos > 0 else 0,
            'percentual_ok': (produtos_ok / total_produtos * 100) if total_produtos > 0 else 0
        }
    
    def gerar_recomendacoes(self, resultado_analise):
        """Gera recomendações baseadas na análise"""
        if resultado_analise is None or len(resultado_analise) == 0:
            return []
        
        recomendacoes = []
        
        # Produtos críticos
        produtos_criticos = resultado_analise[resultado_analise['Situação'] == 'Comprar']
        if len(produtos_criticos) > 0:
            recomendacoes.append({
                'tipo': 'urgente',
                'titulo': 'Produtos Críticos',
                'descricao': f'{len(produtos_criticos)} produtos precisam de reposição urgente',
                'produtos': produtos_criticos.head(5)[['Código', 'Descrição', 'Estoque Restante Estimado']].to_dict('records')
            })
        
        # Produtos com estoque excessivo
        produtos_excessivos = resultado_analise[
            resultado_analise['Estoque Restante Estimado'] > 180
        ]
        if len(produtos_excessivos) > 0:
            recomendacoes.append({
                'tipo': 'excessivo',
                'titulo': 'Estoque Excessivo',
                'descricao': f'{len(produtos_excessivos)} produtos com estoque excessivo',
                'produtos': produtos_excessivos.head(5)[['Código', 'Descrição', 'Estoque Restante Estimado']].to_dict('records')
            })
        
        # Produtos com alta demanda
        produtos_alta_demanda = resultado_analise.nlargest(5, 'Média de Saída Mensal')
        recomendacoes.append({
            'tipo': 'alta_demanda',
            'titulo': 'Produtos de Alta Demanda',
            'descricao': 'Produtos com maior saída mensal',
            'produtos': produtos_alta_demanda[['Código', 'Descrição', 'Média de Saída Mensal']].to_dict('records')
        })
        
        return recomendacoes 