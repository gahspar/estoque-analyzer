import pandas as pd
import numpy as np
import logging
import re
from analise_avancada import AnaliseAvancada

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EstoqueAnalyzer:
    """Analisador de estoque com suporte a análise avançada"""
    
    def __init__(self):
        self.analise_avancada = AnaliseAvancada()
    
    def detectar_linha_inicio(self, df):
        """Detecta automaticamente a linha de início dos dados"""
        for i, row in df.iterrows():
            # Verificar se a linha contém dados numéricos nas colunas esperadas
            valores_numericos = 0
            for col in df.columns:
                try:
                    valor = row[col]
                    if pd.notna(valor) and str(valor).replace('.', '').replace(',', '').replace('-', '').isdigit():
                        valores_numericos += 1
                except:
                    continue
            
            # Se encontrou pelo menos 2 valores numéricos, provavelmente é a linha de dados
            if valores_numericos >= 2:
                return i
        
        return 0
    
    def mapear_colunas_automaticamente(self, df):
        """Mapeia colunas automaticamente baseado no conteúdo"""
        mapeamento = {}
        
        for i, col in enumerate(df.columns):
            col_str = str(col).lower()
            
            # Mapear por nome da coluna
            if 'codigo' in col_str or 'código' in col_str:
                mapeamento['codigo'] = i
            elif 'descricao' in col_str or 'descrição' in col_str or 'produto' in col_str:
                mapeamento['descricao'] = i
            elif 'unidade' in col_str or 'un' in col_str:
                mapeamento['unidade'] = i
            elif 'quantidade' in col_str or 'estoque' in col_str or 'saldo' in col_str:
                mapeamento['quantidade'] = i
            elif 'saida' in col_str or 'saída' in col_str:
                mapeamento['saida'] = i
        
        # Se não encontrou por nome, tentar por conteúdo
        if 'codigo' not in mapeamento:
            for i, col in enumerate(df.columns):
                valores = df[col].dropna().astype(str)
                # Verificar se contém códigos (números)
                if valores.str.match(r'^\d+').sum() > len(valores) * 0.5:
                    mapeamento['codigo'] = i
                    break
        
        if 'descricao' not in mapeamento:
            for i, col in enumerate(df.columns):
                valores = df[col].dropna().astype(str)
                # Verificar se contém texto longo
                if valores.str.len().mean() > 10:
                    mapeamento['descricao'] = i
                    break
        
        if 'quantidade' not in mapeamento:
            for i, col in enumerate(df.columns):
                try:
                    valores = pd.to_numeric(df[col], errors='coerce')
                    if valores.notna().sum() > len(df) * 0.3:
                        mapeamento['quantidade'] = i
                        break
                except:
                    continue
        
        return mapeamento
    
    def carregar_planilha(self, arquivo, linha_inicio=None, mapeamento=None):
        """Carrega e processa uma planilha Excel"""
        try:
            # Carregar planilha
            df = pd.read_excel(arquivo, header=None)
            
            # Detectar linha de início se não especificada
            if linha_inicio is None:
                linha_inicio = self.detectar_linha_inicio(df)
            
            # Pular linhas de cabeçalho
            df_dados = df.iloc[linha_inicio:].reset_index(drop=True)
            
            # Mapear colunas se não especificado
            if mapeamento is None:
                mapeamento = self.mapear_colunas_automaticamente(df_dados)
            
            # Extrair dados
            dados = {}
            
            if 'codigo' in mapeamento and 'descricao' in mapeamento:
                # Combinar código e descrição
                codigos = df_dados.iloc[:, mapeamento['codigo']].astype(str)
                descricoes = df_dados.iloc[:, mapeamento['descricao']].astype(str)
                dados['codigo_descricao'] = codigos + ' - ' + descricoes
            elif 'codigo' in mapeamento:
                dados['codigo_descricao'] = df_dados.iloc[:, mapeamento['codigo']].astype(str)
            elif 'descricao' in mapeamento:
                dados['codigo_descricao'] = df_dados.iloc[:, mapeamento['descricao']].astype(str)
            
            if 'unidade' in mapeamento:
                dados['unidade'] = df_dados.iloc[:, mapeamento['unidade']].astype(str)
            
            if 'quantidade' in mapeamento:
                dados['quantidade'] = pd.to_numeric(df_dados.iloc[:, mapeamento['quantidade']], errors='coerce')
            
            if 'saida' in mapeamento:
                dados['saida'] = pd.to_numeric(df_dados.iloc[:, mapeamento['saida']], errors='coerce')
            
            # Criar DataFrame
            df_final = pd.DataFrame(dados)
            
            # Limpar dados
            df_final = df_final.dropna(subset=['codigo_descricao'])
            df_final = df_final[df_final['codigo_descricao'].str.strip() != '']
            
            return df_final
            
        except Exception as e:
            logger.error(f"Erro ao carregar planilha: {str(e)}")
            return None
    
    def analisar_estoque(self, estoque_file, saidas_file, config_manual=None, tipo_produto='medicamentos', media_pacientes=None):
        """Analisa estoque com suporte a análise avançada"""
        try:
            # Configurar análise avançada
            self.analise_avancada.configurar_tipo_produto(tipo_produto, media_pacientes)
            
            # Configurações manuais
            linha_inicio_estoque = config_manual.get('linha_inicio_estoque', None) if config_manual else None
            linha_inicio_saidas = config_manual.get('linha_inicio_saidas', None) if config_manual else None
            mapeamento_estoque = config_manual.get('mapeamento_estoque', None) if config_manual else None
            mapeamento_saidas = config_manual.get('mapeamento_saidas', None) if config_manual else None
            
            # Carregar planilhas
            df_estoque = self.carregar_planilha(estoque_file, linha_inicio_estoque, mapeamento_estoque)
            df_saidas = self.carregar_planilha(saidas_file, linha_inicio_saidas, mapeamento_saidas)
            
            if df_estoque is None or df_saidas is None:
                return None
            
            logger.info(f"Planilha estoque carregada com {len(df_estoque)} registros")
            logger.info(f"Planilha saidas carregada com {len(df_saidas)} registros")
            
            # Processar dados de estoque
            df_estoque['codigo'] = df_estoque['codigo_descricao'].str.extract(r'(\d+)').astype(str)
            df_estoque['descricao'] = df_estoque['codigo_descricao'].str.replace(r'^\d+\s*-\s*', '', regex=True)
            
            # Processar dados de saídas
            df_saidas['codigo'] = df_saidas['codigo_descricao'].str.extract(r'(\d+)').astype(str)
            df_saidas['descricao'] = df_saidas['codigo_descricao'].str.replace(r'^\d+\s*-\s*', '', regex=True)
            
            # Encontrar produtos em comum
            produtos_comuns = set(df_estoque['codigo']) & set(df_saidas['codigo'])
            logger.info(f"Produtos encontrados em ambas as planilhas: {len(produtos_comuns)}")
            
            if len(produtos_comuns) == 0:
                return None
            
            # Criar resultado
            resultados = []
            
            for codigo in produtos_comuns:
                # Dados do estoque
                estoque_produto = df_estoque[df_estoque['codigo'] == codigo].iloc[0]
                estoque_atual = estoque_produto.get('quantidade', 0)
                descricao = estoque_produto.get('descricao', '')
                unidade = estoque_produto.get('unidade', '')
                
                # Dados das saídas
                saidas_produto = df_saidas[df_saidas['codigo'] == codigo]
                media_saida_mensal = saidas_produto.get('saida', pd.Series([0])).mean()
                
                # Calcular demanda esperada com análise avançada
                demanda_esperada = self.analise_avancada.calcular_demanda_esperada(media_saida_mensal)
                
                # Calcular estoque restante
                estoque_restante = estoque_atual - demanda_esperada
                
                # Determinar situação
                if estoque_restante < 0:
                    situacao = 'Comprar'
                else:
                    situacao = 'OK'
                
                # Calcular prazo de estoque
                prazo_estoque = self.analise_avancada.calcular_prazo_estoque(estoque_atual, demanda_esperada)
                
                # Sugerir quantidade para compra
                quantidade_sugerida = self.analise_avancada.sugerir_quantidade_compra(
                    estoque_atual, demanda_esperada
                )
                
                resultados.append({
                    'Código': codigo,
                    'Descrição': descricao,
                    'Unidade': unidade,
                    'Quantidade em estoque': estoque_atual,
                    'Média de Saída Mensal': media_saida_mensal,
                    'Demanda Esperada': demanda_esperada,
                    'Estoque Restante Estimado': estoque_restante,
                    'Prazo Estoque (dias)': prazo_estoque,
                    'Quantidade Sugerida Compra': quantidade_sugerida,
                    'Situação': situacao
                })
            
            df_resultado = pd.DataFrame(resultados)
            
            # Adicionar informações de análise avançada
            df_resultado['Tipo Produto'] = tipo_produto
            if media_pacientes:
                df_resultado['Média Pacientes'] = media_pacientes
            
            return df_resultado
            
        except Exception as e:
            logger.error(f"Erro na análise: {str(e)}")
            return None 