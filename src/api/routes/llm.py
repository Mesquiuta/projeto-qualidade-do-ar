"""
Rota para análise de dados de qualidade do ar usando LLM (Gemini).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import google.generativeai as genai

router = APIRouter()

# Configurar Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


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
    Analisa dados de qualidade do ar usando LLM (Gemini) e retorna recomendações.
    
    Args:
        request: Dados de qualidade do ar para análise
        
    Returns:
        Análise e recomendações geradas pelo LLM
    """
    try:
        # Verificar se a API key está configurada
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY não configurada"
            )
        
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

        # Chamar Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Extrair resposta
        llm_response = response.text
        
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
    Endpoint de teste para verificar se o LLM (Gemini) está funcionando.
    """
    try:
        # Verificar se a API key está configurada
        if not GEMINI_API_KEY:
            return {
                "status": "error",
                "message": "GEMINI_API_KEY não configurada",
                "response": None
            }
        
        # Testar Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Responda apenas 'OK - Gemini funcionando!' se você está operacional.")
        
        return {
            "status": "success",
            "message": "Gemini está funcionando corretamente",
            "response": response.text,
            "model": "gemini-1.5-flash"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao testar Gemini: {str(e)}"
        )
