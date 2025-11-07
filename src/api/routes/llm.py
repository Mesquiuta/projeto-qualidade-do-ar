"""
Rota para análise de dados de qualidade do ar usando LLM.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from openai import OpenAI

router = APIRouter()

# Inicializar cliente OpenAI
client = OpenAI()


class AirQualityAnalysisRequest(BaseModel):
    """Request para análise de qualidade do ar."""
    pm25: float
    pm10: float
    city: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None


class AirQualityAnalysisResponse(BaseModel):
    """Response da análise de qualidade do ar."""
    analysis: str
    recommendations: str


@router.post("/analyze", response_model=AirQualityAnalysisResponse)
async def analyze_air_quality(request: AirQualityAnalysisRequest):
    """
    Analisa dados de qualidade do ar usando LLM e retorna recomendações.
    
    Args:
        request: Dados de qualidade do ar para análise
        
    Returns:
        Análise e recomendações geradas pelo LLM
    """
    try:
        # Construir prompt com os dados
        prompt = f"""Analise os seguintes dados de qualidade do ar para a cidade de {request.city}:

- PM2.5: {request.pm25} µg/m³
- PM10: {request.pm10} µg/m³"""

        if request.temperature is not None:
            prompt += f"\n- Temperatura: {request.temperature}°C"
        
        if request.humidity is not None:
            prompt += f"\n- Umidade: {request.humidity}%"

        prompt += """

Por favor, forneça:
1. Uma análise breve sobre a qualidade do ar (2-3 frases)
2. Recomendações práticas para a população (2-3 itens)

Seja direto e objetivo."""

        # Chamar LLM
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em qualidade do ar e saúde pública. Forneça análises claras e recomendações práticas baseadas nos dados de poluição do ar."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        # Extrair resposta
        llm_response = response.choices[0].message.content
        
        # Separar análise e recomendações (formato simples)
        parts = llm_response.split("\n\n")
        
        if len(parts) >= 2:
            analysis = parts[0]
            recommendations = "\n\n".join(parts[1:])
        else:
            analysis = llm_response
            recommendations = "Consulte as autoridades de saúde locais para mais informações."
        
        return AirQualityAnalysisResponse(
            analysis=analysis.strip(),
            recommendations=recommendations.strip()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar análise: {str(e)}"
        )


@router.get("/test")
async def test_llm():
    """
    Endpoint de teste para verificar se o LLM está funcionando.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "user",
                    "content": "Responda apenas 'OK' se você está funcionando."
                }
            ],
            max_tokens=10
        )
        
        return {
            "status": "success",
            "message": "LLM está funcionando corretamente",
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao testar LLM: {str(e)}"
        )
