"""
Script simples para testar a funcionalidade LLM com Gemini.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import google.generativeai as genai

# Criar app FastAPI
app = FastAPI(title="Teste LLM - Qualidade do Ar (Gemini)")

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


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "message": "API de Teste - Análise de Qualidade do Ar com Gemini",
        "endpoints": {
            "test": "/test",
            "analyze": "/analyze"
        }
    }


@app.get("/test")
async def test_llm():
    """
    Endpoint de teste para verificar se o Gemini está funcionando.
    """
    try:
        if not GEMINI_API_KEY:
            return {
                "status": "error",
                "message": "GEMINI_API_KEY não configurada. Configure a variável de ambiente."
            }
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Responda apenas 'OK - Gemini funcionando!' se você está operacional.")
        
        return {
            "status": "success",
            "message": "Gemini está funcionando corretamente",
            "response": response.text,
            "model": "gemini-1.5-flash"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao testar Gemini: {str(e)}"
        }


@app.post("/analyze", response_model=AirQualityAnalysisResponse)
async def analyze_air_quality(request: AirQualityAnalysisRequest):
    """
    Analisa dados de qualidade do ar usando Gemini e retorna recomendações.
    """
    try:
        if not GEMINI_API_KEY:
            return AirQualityAnalysisResponse(
                analysis="Erro: GEMINI_API_KEY não configurada",
                recommendations="Configure a variável de ambiente GEMINI_API_KEY"
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
        
        # Separar análise e recomendações
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
        return AirQualityAnalysisResponse(
            analysis=f"Erro ao processar análise: {str(e)}",
            recommendations="Não foi possível gerar recomendações."
        )


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de teste LLM com Gemini...")
    print("📍 Acesse: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("")
    if not GEMINI_API_KEY:
        print("⚠️  ATENÇÃO: GEMINI_API_KEY não configurada!")
        print("   Configure com: export GEMINI_API_KEY='sua-chave-aqui'")
    else:
        print("✅ GEMINI_API_KEY configurada")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)
