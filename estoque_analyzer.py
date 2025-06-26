import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, List, Any
import logging
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EstoqueAnalyzer:
    """
    Classe responsável por analisar dados de estoque e saídas mensais.
    """
    
    def __init__(self):
        """Inicializa o analisador de estoque."""
        self.colunas_padrao = ['Código do produto', 'Descrição', 'Unidade de medida', 'Quantidade em estoque', 'Quantidade de saídas']
    
    def detectar_inicio_dados(self, df: pd.DataFrame, tipo: str) -> int:
        """
        Detecta automaticamente a primeira linha de dados reais.
        Baseado na análise das planilhas reais, os dados começam na linha 15.
        """
        # Procurar por padrão específico: linha com "Un." na coluna 11 e "Quantidade" na coluna 14
        for i in range(len(df)):
            linha = df.iloc[i]
            if (pd.notna(linha.get(11)) and str(linha.get(11)).strip() == 'Un.' and 
                pd.notna(linha.get(14)) and 'Quantidade' in str(linha.get(14))):
                return i + 2  # Dados começam 2 linhas depois do header
        return 15  # Fallback baseado na análise

    def extrair_codigo_descricao(self, texto: str) -> tuple:
        """
        Extrai código e descrição de um texto como "151 - DIPIRONA SODICA 0,5MG/ML"
        """
        if pd.isna(texto) or not isinstance(texto, str):
            return None, None
        
        texto = texto.strip()
        # Padrão: número - descrição
        match = re.match(r'(\d+)\s*-\s*(.+)', texto)
        if match:
            return match.group(1), match.group(2).strip()
        return None, texto

    def carregar_planilha(self, arquivo, tipo: str, linha_inicio: Optional[int]=None, mapeamento_colunas: Optional[Dict[str, int]]=None) -> Optional[pd.DataFrame]:
        """
        Carrega a planilha, detectando automaticamente o início dos dados e as colunas.
        """
        try:
            df = pd.read_excel(arquivo, header=None)
            
            if linha_inicio is None:
                linha_inicio = self.detectar_inicio_dados(df, tipo)
            
            dados = df.iloc[linha_inicio:]
            dados = dados.reset_index(drop=True)
            
            # Mapeamento específico baseado na análise das planilhas reais
            if mapeamento_colunas is None:
                mapeamento_colunas = {
                    'codigo_descricao': 0,  # Coluna 0: "151 - DIPIRONA SODICA 0,5MG/ML"
                    'unidade': 11,          # Coluna 11: "AMP", "COM", "FCO", "UND"
                    'quantidade': 14        # Coluna 14: quantidade numérica
                }
            
            # Montar DataFrame padronizado
            df_final = pd.DataFrame()
            
            # Extrair código e descrição da coluna 0
            codigos = []
            descricoes = []
            for valor in dados[mapeamento_colunas['codigo_descricao']]:
                codigo, descricao = self.extrair_codigo_descricao(valor)
                codigos.append(codigo)
                descricoes.append(descricao)
            
            df_final['Código do produto'] = codigos
            df_final['Descrição'] = descricoes
            df_final['Unidade de medida'] = dados[mapeamento_colunas['unidade']]
            
            if tipo == 'estoque':
                df_final['Quantidade em estoque'] = dados[mapeamento_colunas['quantidade']]
            else:
                df_final['Quantidade de saídas'] = dados[mapeamento_colunas['quantidade']]
            
            # Limpar dados
            df_final = self._limpar_dados(df_final, tipo)
            
            logger.info(f"Planilha {tipo} carregada com {len(df_final)} registros")
            return df_final
            
        except Exception as e:
            logger.error(f"Erro ao carregar planilha: {e}")
            return None

    def _limpar_dados(self, df: pd.DataFrame, tipo: str) -> pd.DataFrame:
        """
        Limpa e prepara os dados da planilha.
        """
        # Remover linhas onde código do produto está vazio
        df = df.dropna(subset=['Código do produto'])
        
        # Remover linhas com "Total" ou outros textos que não são produtos
        df = df[df['Código do produto'].astype(str).str.strip() != 'Total']
        df = df[df['Código do produto'].astype(str).str.strip() != 'nan']
        
        # Remover duplicatas baseado no código do produto
        df = df.drop_duplicates(subset=['Código do produto'])
        
        # Converter colunas numéricas
        if tipo == 'estoque':
            df['Quantidade em estoque'] = pd.to_numeric(df['Quantidade em estoque'], errors='coerce')
            df = df[df['Quantidade em estoque'] >= 0]
        else:
            df['Quantidade de saídas'] = pd.to_numeric(df['Quantidade de saídas'], errors='coerce')
            df = df[df['Quantidade de saídas'] >= 0]
        
        return df

    def analisar_estoque(self, arquivo_estoque, arquivo_saidas, config_manual: Optional[Dict[str, Any]]=None) -> Optional[pd.DataFrame]:
        """
        Analisa o estoque comparando com as saídas mensais.
        """
        try:
            if config_manual:
                df_estoque = self.carregar_planilha(arquivo_estoque, 'estoque', config_manual.get('linha_inicio_estoque'), config_manual.get('mapeamento_estoque'))
                df_saidas = self.carregar_planilha(arquivo_saidas, 'saidas', config_manual.get('linha_inicio_saidas'), config_manual.get('mapeamento_saidas'))
            else:
                df_estoque = self.carregar_planilha(arquivo_estoque, 'estoque')
                df_saidas = self.carregar_planilha(arquivo_saidas, 'saidas')
            
            if df_estoque is None or df_saidas is None:
                return None
            
            resultado = self._processar_analise(df_estoque, df_saidas)
            return resultado
            
        except Exception as e:
            logger.error(f"Erro durante análise: {e}")
            return None

    def _processar_analise(self, df_estoque: pd.DataFrame, df_saidas: pd.DataFrame) -> pd.DataFrame:
        """
        Processa a análise comparando estoque e saídas.
        """
        # Fazer merge das planilhas baseado no código do produto
        df_merge = pd.merge(
            df_estoque,
            df_saidas,
            on='Código do produto',
            how='inner',
            suffixes=('_estoque', '_saidas')
        )
        
        logger.info(f"Produtos encontrados em ambas as planilhas: {len(df_merge)}")
        
        if len(df_merge) == 0:
            raise ValueError("Nenhum produto encontrado em ambas as planilhas")
        
        # Calcular média de saída mensal (assumindo que os dados representam 1 mês)
        df_merge['Média de Saída Mensal'] = df_merge['Quantidade de saídas']
        
        # Calcular estoque restante estimado
        df_merge['Estoque Restante Estimado'] = (
            df_merge['Quantidade em estoque'] - df_merge['Média de Saída Mensal']
        )
        
        # Determinar situação
        df_merge['Situação'] = np.where(
            df_merge['Quantidade em estoque'] > df_merge['Média de Saída Mensal'],
            'OK',
            'Comprar'
        )
        
        # Selecionar e renomear colunas para o resultado final
        resultado = df_merge[[
            'Código do produto',
            'Descrição_estoque',
            'Quantidade em estoque',
            'Média de Saída Mensal',
            'Estoque Restante Estimado',
            'Situação'
        ]].copy()
        
        # Renomear coluna de descrição
        resultado = resultado.rename(columns={'Descrição_estoque': 'Descrição'})
        
        # Ordenar por situação (Comprar primeiro) e depois por código
        resultado = resultado.sort_values(['Situação', 'Código do produto'])
        
        return resultado
    
    def gerar_relatorio_detalhado(self, resultado: pd.DataFrame) -> dict:
        """
        Gera um relatório detalhado com estatísticas da análise.
        
        Args:
            resultado: DataFrame com os resultados da análise
            
        Returns:
            Dicionário com estatísticas detalhadas
        """
        total_produtos = len(resultado)
        produtos_ok = len(resultado[resultado['Situação'] == 'OK'])
        produtos_comprar = len(resultado[resultado['Situação'] == 'Comprar'])
        
        # Estatísticas de estoque
        estoque_total = resultado['Quantidade em Estoque'].sum()
        estoque_ok = resultado[resultado['Situação'] == 'OK']['Quantidade em Estoque'].sum()
        estoque_comprar = resultado[resultado['Situação'] == 'Comprar']['Quantidade em Estoque'].sum()
        
        # Estatísticas de saída
        saida_total = resultado['Média de Saída Mensal'].sum()
        saida_ok = resultado[resultado['Situação'] == 'OK']['Média de Saída Mensal'].sum()
        saida_comprar = resultado[resultado['Situação'] == 'Comprar']['Média de Saída Mensal'].sum()
        
        # Produtos com maior risco (estoque muito baixo)
        risco_alto = resultado[
            resultado['Estoque Restante Estimado'] < 0
        ].sort_values('Estoque Restante Estimado')
        
        # Produtos com estoque excessivo (mais de 3x a saída média)
        estoque_excessivo = resultado[
            resultado['Quantidade em Estoque'] > (resultado['Média de Saída Mensal'] * 3)
        ].sort_values('Quantidade em Estoque', ascending=False)
        
        return {
            'resumo': {
                'total_produtos': total_produtos,
                'produtos_ok': produtos_ok,
                'produtos_comprar': produtos_comprar,
                'percentual_ok': (produtos_ok / total_produtos * 100) if total_produtos > 0 else 0,
                'percentual_comprar': (produtos_comprar / total_produtos * 100) if total_produtos > 0 else 0
            },
            'estoque': {
                'total': estoque_total,
                'ok': estoque_ok,
                'comprar': estoque_comprar
            },
            'saidas': {
                'total': saida_total,
                'ok': saida_ok,
                'comprar': saida_comprar
            },
            'risco_alto': risco_alto,
            'estoque_excessivo': estoque_excessivo
        } 