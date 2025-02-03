# Valencia SME Solutions - Product Guide
# Valencia SME Solutions - Guía del Producto

[English](#english) | [Español](#español)

# English

## Product Overview

Valencia SME Solutions is an advanced business analytics platform powered by Claude-3 AI that provides comprehensive market intelligence and strategic recommendations for small and medium-sized enterprises (SMEs).

## Integration Guide

### 1. API Integration

Our REST API provides programmatic access to all analysis features.

#### Base URL
```
http://localhost:5000/api/v1
```

#### Authentication
Include your API key in the request headers:
```
Authorization: Bearer YOUR_API_KEY
```

#### Endpoints

1. **Analyze Business**
```
POST /analyze/{analysis_type}

analysis_type options:
- pricing
- sentiment
- competitors
- forecast

Request Body:
{
    "business_name": "Your Business Name",
    "business_type": "restaurant|hotel|attraction"
}

Response:
{
    "analysis": {
        "summary": "Analysis summary",
        "recommendations": ["Recommendation 1", "Recommendation 2"],
        "metrics": {
            "metric1": "value1",
            "metric2": "value2"
        }
    }
}
```

### 2. Web Integration

#### Option 1: Embed Analysis Form
```html
<!-- Add this where you want the analysis form to appear -->
<iframe src="http://localhost:5000/web/index.html" 
        width="100%" 
        height="800px" 
        frameborder="0">
</iframe>
```

#### Option 2: Custom Integration
1. Include our required files:
```html
<link href="styles.css" rel="stylesheet">
<script src="translations.js"></script>
<script src="app.js"></script>
```

2. Add the analysis form:
```html
<div id="vsme-analysis-form">
    <!-- Form will be automatically inserted here -->
</div>
```

## Implementation Steps

1. **API Setup**
   ```bash
   # Install dependencies
   pip install flask flask-cors python-dotenv

   # Start the API server
   python api/app.py
   ```

2. **Web Integration**
   - Copy the web directory to your server
   - Update API endpoint in app.js if needed
   - Open index.html in a browser

## Support

For technical support:
- Email: support@valenciasme.com
- Documentation: This guide
- API Status: http://localhost:5000/status

---

# Español

## Descripción del Producto

Valencia SME Solutions es una plataforma avanzada de análisis empresarial impulsada por IA Claude-3 que proporciona inteligencia de mercado integral y recomendaciones estratégicas para pequeñas y medianas empresas (PYMES).

## Guía de Integración

### 1. Integración de API

Nuestra API REST proporciona acceso programático a todas las funciones de análisis.

#### URL Base
```
http://localhost:5000/api/v1
```

#### Autenticación
Incluya su clave API en los encabezados de la solicitud:
```
Authorization: Bearer SU_CLAVE_API
```

#### Endpoints

1. **Analizar Negocio**
```
POST /analyze/{tipo_analisis}

Opciones de tipo_analisis:
- pricing (precios)
- sentiment (sentimiento)
- competitors (competidores)
- forecast (pronóstico)

Cuerpo de la Solicitud:
{
    "business_name": "Nombre de su Negocio",
    "business_type": "restaurant|hotel|attraction"
}

Respuesta:
{
    "analysis": {
        "resumen": "Resumen del análisis",
        "recomendaciones": ["Recomendación 1", "Recomendación 2"],
        "metricas": {
            "metrica1": "valor1",
            "metrica2": "valor2"
        }
    }
}
```

### 2. Integración Web

#### Opción 1: Insertar Formulario de Análisis
```html
<!-- Agregue esto donde desee que aparezca el formulario de análisis -->
<iframe src="http://localhost:5000/web/index.html" 
        width="100%" 
        height="800px" 
        frameborder="0">
</iframe>
```

#### Opción 2: Integración Personalizada
1. Incluya nuestros archivos requeridos:
```html
<link href="styles.css" rel="stylesheet">
<script src="translations.js"></script>
<script src="app.js"></script>
```

2. Agregue el formulario de análisis:
```html
<div id="vsme-analysis-form">
    <!-- El formulario se insertará automáticamente aquí -->
</div>
```

## Pasos de Implementación

1. **Configuración de API**
   ```bash
   # Instalar dependencias
   pip install flask flask-cors python-dotenv

   # Iniciar el servidor API
   python api/app.py
   ```

2. **Integración Web**
   - Copie el directorio web a su servidor
   - Actualice el endpoint de API en app.js si es necesario
   - Abra index.html en un navegador

## Soporte

Para soporte técnico:
- Email: support@valenciasme.com
- Documentación: Esta guía
- Estado de API: http://localhost:5000/status
