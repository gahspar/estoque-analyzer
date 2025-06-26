"""
Script para gerar planilhas de exemplo para demonstração da aplicação.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def criar_planilha_estoque():
    """Cria uma planilha de exemplo com dados de estoque atual."""
    
    # Dados de exemplo
    dados_estoque = {
        'Código do produto': [
            'PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD005',
            'PROD006', 'PROD007', 'PROD008', 'PROD009', 'PROD010'
        ],
        'Descrição': [
            'Arroz Integral 1kg',
            'Feijão Preto 500g',
            'Óleo de Soja 900ml',
            'Macarrão Espaguete 500g',
            'Café em Pó 500g',
            'Açúcar Refinado 1kg',
            'Farinha de Trigo 1kg',
            'Leite Condensado 395g',
            'Molho de Tomate 340g',
            'Sal Refinado 1kg'
        ],
        'Unidade de medida': [
            'kg', 'g', 'ml', 'g', 'g', 'kg', 'kg', 'g', 'g', 'kg'
        ],
        'Quantidade em estoque': [
            150, 200, 80, 120, 90, 300, 180, 60, 100, 250
        ]
    }
    
    df_estoque = pd.DataFrame(dados_estoque)
    
    # Salvar arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"estoque_exemplo_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df_estoque.to_excel(writer, sheet_name='Estoque Atual', index=False)
        
        # Formatação
        workbook = writer.book
        worksheet = writer.sheets['Estoque Atual']
        
        # Formato do cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Aplicar formatação
        for col_num, value in enumerate(df_estoque.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ajustar largura das colunas
        for i, col in enumerate(df_estoque.columns):
            max_len = max(
                df_estoque[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.set_column(i, i, max_len + 2)
    
    print(f"✅ Planilha de estoque criada: {filename}")
    return filename

def criar_planilha_saidas():
    """Cria uma planilha de exemplo com dados de saídas mensais."""
    
    # Dados de exemplo
    dados_saidas = {
        'Código do produto': [
            'PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD005',
            'PROD006', 'PROD007', 'PROD008', 'PROD009', 'PROD010'
        ],
        'Descrição': [
            'Arroz Integral 1kg',
            'Feijão Preto 500g',
            'Óleo de Soja 900ml',
            'Macarrão Espaguete 500g',
            'Café em Pó 500g',
            'Açúcar Refinado 1kg',
            'Farinha de Trigo 1kg',
            'Leite Condensado 395g',
            'Molho de Tomate 340g',
            'Sal Refinado 1kg'
        ],
        'Unidade de medida': [
            'kg', 'g', 'ml', 'g', 'g', 'kg', 'kg', 'g', 'g', 'kg'
        ],
        'Quantidade de saídas': [
            180, 150, 120, 100, 110, 200, 160, 80, 90, 180
        ]
    }
    
    df_saidas = pd.DataFrame(dados_saidas)
    
    # Salvar arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saidas_exemplo_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df_saidas.to_excel(writer, sheet_name='Saídas Mensais', index=False)
        
        # Formatação
        workbook = writer.book
        worksheet = writer.sheets['Saídas Mensais']
        
        # Formato do cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Aplicar formatação
        for col_num, value in enumerate(df_saidas.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ajustar largura das colunas
        for i, col in enumerate(df_saidas.columns):
            max_len = max(
                df_saidas[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.set_column(i, i, max_len + 2)
    
    print(f"✅ Planilha de saídas criada: {filename}")
    return filename

def criar_planilhas_exemplo():
    """Cria ambas as planilhas de exemplo."""
    print("📊 Criando planilhas de exemplo...")
    
    estoque_file = criar_planilha_estoque()
    saidas_file = criar_planilha_saidas()
    
    print("\n📋 Planilhas criadas com sucesso!")
    print(f"📁 Estoque: {estoque_file}")
    print(f"📁 Saídas: {saidas_file}")
    print("\n💡 Use essas planilhas para testar a aplicação de análise de estoque.")
    
    return estoque_file, saidas_file

if __name__ == "__main__":
    criar_planilhas_exemplo() 