#!/usr/bin/env python3
"""
Script para coleta de dados de qualidade do ar e meteorológicos.
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import logging

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.data.collectors import DataCollectionManager, OpenAQCollector, INMETCollector
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def collect_openaq_data(
    cities: list,
    parameters: list,
    days_back: int,
    output_dir: Path
) -> None:
    """
    Coleta dados da API OpenAQ.
    """
    logger.info(f"Coletando dados OpenAQ para {len(cities)} cidades...")
    
    async with OpenAQCollector() as collector:
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        for city in cities:
            logger.info(f"Coletando dados para {city}...")
            
            city_data = {}
            
            for parameter in parameters:
                try:
                    df = await collector.get_measurements(
                        city=city,
                        parameter=parameter,
                        date_from=start_date,
                        date_to=end_date,
                        limit=days_back * 24  # Aproximadamente dados horários
                    )
                    
                    if not df.empty:
                        city_data[parameter] = df
                        logger.info(f"  {parameter}: {len(df)} registros")
                    else:
                        logger.warning(f"  {parameter}: Nenhum dado encontrado")
                        
                except Exception as e:
                    logger.error(f"  Erro ao coletar {parameter}: {e}")
            
            # Salvar dados da cidade
            if city_data:
                city_dir = output_dir / "openaq" / city.replace(" ", "_").lower()
                city_dir.mkdir(parents=True, exist_ok=True)
                
                for parameter, df in city_data.items():
                    filename = f"{parameter}_{start_date}_{end_date}.csv"
                    filepath = city_dir / filename
                    df.to_csv(filepath, index=False)
                    logger.info(f"  Salvo: {filepath}")


def collect_inmet_data(
    cities: list,
    days_back: int,
    output_dir: Path
) -> None:
    """
    Coleta dados do INMET.
    """
    logger.info(f"Coletando dados INMET para {len(cities)} cidades...")
    
    collector = INMETCollector()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    # Obter lista de estações
    stations_df = collector.get_stations()
    
    if stations_df.empty:
        logger.error("Não foi possível obter lista de estações INMET")
        return
    
    for city in cities:
        logger.info(f"Coletando dados meteorológicos para {city}...")
        
        try:
            # Encontrar estação mais próxima
            station_code = collector.find_nearest_station(city, "SP")
            
            if not station_code:
                logger.warning(f"  Estação não encontrada para {city}")
                continue
            
            # Coletar dados históricos
            df = collector.get_historical_data(station_code, start_date, end_date)
            
            if not df.empty:
                # Salvar dados
                city_dir = output_dir / "inmet" / city.replace(" ", "_").lower()
                city_dir.mkdir(parents=True, exist_ok=True)
                
                filename = f"weather_{start_date}_{end_date}.csv"
                filepath = city_dir / filename
                df.to_csv(filepath)
                
                logger.info(f"  Salvo: {filepath} ({len(df)} registros)")
            else:
                logger.warning(f"  Nenhum dado encontrado para {city}")
                
        except Exception as e:
            logger.error(f"  Erro ao coletar dados para {city}: {e}")


async def collect_combined_data(
    cities: list,
    days_back: int,
    output_dir: Path
) -> None:
    """
    Coleta dados combinados usando o DataCollectionManager.
    """
    logger.info(f"Coletando dados combinados para {len(cities)} cidades...")
    
    manager = DataCollectionManager()
    
    # Preparar lista de cidades
    city_list = [{'name': city, 'state': 'SP'} for city in cities]
    
    # Coletar dados
    all_data = await manager.collect_multiple_cities(city_list, days_back)
    
    # Salvar dados combinados
    for city, data in all_data.items():
        logger.info(f"Processando dados combinados para {city}...")
        
        city_dir = output_dir / "combined" / city.replace(" ", "_").lower()
        city_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar dados de poluição
        if not data['pollution'].empty:
            pollution_file = city_dir / "pollution.csv"
            data['pollution'].to_csv(pollution_file, index=False)
            logger.info(f"  Poluição salva: {pollution_file} ({len(data['pollution'])} registros)")
        
        # Salvar dados meteorológicos
        if not data['weather'].empty:
            weather_file = city_dir / "weather.csv"
            data['weather'].to_csv(weather_file)
            logger.info(f"  Clima salvo: {weather_file} ({len(data['weather'])} registros)")
        
        # Criar dataset combinado se ambos existirem
        if not data['pollution'].empty and not data['weather'].empty:
            try:
                # Alinhar dados por timestamp
                merged = pd.merge_asof(
                    data['pollution'].sort_values('datetime'),
                    data['weather'].sort_values('datetime'),
                    on='datetime',
                    direction='nearest'
                )
                
                if not merged.empty:
                    combined_file = city_dir / "combined.csv"
                    merged.to_csv(combined_file, index=False)
                    logger.info(f"  Combinado salvo: {combined_file} ({len(merged)} registros)")
                    
            except Exception as e:
                logger.error(f"  Erro ao combinar dados para {city}: {e}")


def download_historical_files(
    years: list,
    output_dir: Path
) -> None:
    """
    Baixa arquivos históricos do INMET.
    """
    logger.info(f"Baixando arquivos históricos para os anos: {years}")
    
    collector = INMETCollector()
    
    for year in years:
        logger.info(f"Baixando dados de {year}...")
        
        try:
            downloaded_files = collector.download_historical_files(
                year=year,
                save_path=output_dir / "inmet_historical"
            )
            
            if downloaded_files:
                logger.info(f"  Baixados {len(downloaded_files)} arquivos para {year}")
                for file_path in downloaded_files:
                    logger.info(f"    {file_path}")
            else:
                logger.warning(f"  Nenhum arquivo baixado para {year}")
                
        except Exception as e:
            logger.error(f"  Erro ao baixar dados de {year}: {e}")


def generate_collection_report(output_dir: Path) -> None:
    """
    Gera relatório da coleta de dados.
    """
    logger.info("Gerando relatório da coleta...")
    
    report = {
        'timestamp': pd.Timestamp.now(),
        'directories': {},
        'total_files': 0,
        'total_size_mb': 0
    }
    
    # Analisar diretórios
    for source_dir in ['openaq', 'inmet', 'combined', 'inmet_historical']:
        source_path = output_dir / source_dir
        
        if source_path.exists():
            files = list(source_path.rglob('*.csv'))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            report['directories'][source_dir] = {
                'files_count': len(files),
                'size_mb': total_size / (1024 * 1024),
                'cities': len(list(source_path.iterdir())) if source_path.is_dir() else 0
            }
            
            report['total_files'] += len(files)
            report['total_size_mb'] += total_size / (1024 * 1024)
    
    # Salvar relatório
    report_file = output_dir / "collection_report.json"
    
    import json
    with open(report_file, 'w') as f:
        # Converter Timestamp para string para serialização JSON
        report_copy = report.copy()
        report_copy['timestamp'] = report['timestamp'].isoformat()
        json.dump(report_copy, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Relatório salvo: {report_file}")
    
    # Exibir resumo
    print("\n=== Relatório da Coleta ===")
    print(f"Total de arquivos: {report['total_files']}")
    print(f"Tamanho total: {report['total_size_mb']:.2f} MB")
    print("\nPor fonte:")
    for source, info in report['directories'].items():
        print(f"  {source}: {info['files_count']} arquivos, {info['size_mb']:.2f} MB")


async def main():
    """
    Função principal do script.
    """
    parser = argparse.ArgumentParser(description='Coletar dados de qualidade do ar')
    
    parser.add_argument('--cities', nargs='+', 
                       default=['São Paulo', 'Rio de Janeiro', 'Belo Horizonte'],
                       help='Cidades para coleta de dados')
    
    parser.add_argument('--days', type=int, default=30,
                       help='Número de dias de dados históricos')
    
    parser.add_argument('--parameters', nargs='+',
                       default=['pm25', 'pm10', 'no2', 'o3'],
                       help='Parâmetros de poluição para coletar')
    
    parser.add_argument('--output', type=str, default='data/raw',
                       help='Diretório de saída para os dados')
    
    parser.add_argument('--source', choices=['openaq', 'inmet', 'combined', 'historical', 'all'],
                       default='all', help='Fonte de dados para coletar')
    
    parser.add_argument('--years', nargs='+', type=int,
                       help='Anos para download de dados históricos (apenas para --source historical)')
    
    parser.add_argument('--report', action='store_true',
                       help='Gerar relatório da coleta')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(log_level='INFO')
    
    # Criar diretório de saída
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if args.source in ['openaq', 'all']:
            await collect_openaq_data(
                args.cities, args.parameters, args.days, output_dir
            )
        
        if args.source in ['inmet', 'all']:
            collect_inmet_data(args.cities, args.days, output_dir)
        
        if args.source in ['combined', 'all']:
            await collect_combined_data(args.cities, args.days, output_dir)
        
        if args.source == 'historical':
            if not args.years:
                logger.error("Anos devem ser especificados para coleta histórica")
                sys.exit(1)
            
            download_historical_files(args.years, output_dir)
        
        # Gerar relatório se solicitado
        if args.report:
            generate_collection_report(output_dir)
        
        logger.info("Coleta de dados concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a coleta: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
