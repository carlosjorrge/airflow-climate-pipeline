# Pipeline de Dados Climáticos com Apache Airflow

## Visão Geral

Este repositório contém um **pipeline de dados batch orquestrado com Apache Airflow**, responsável por **extrair, tratar e consolidar dados climáticos históricos** a partir da API pública **Open-Meteo**.

O projeto foi desenvolvido com foco em **boas práticas de Engenharia de Dados**, simulando uma arquitetura de **Data Lake em camadas**, com separação clara entre dados brutos, dados tratados e dados prontos para análise.

O objetivo principal do projeto é **demonstrar capacidade técnica prática em pipelines de dados**, incluindo:

* Orquestração com Airflow
* Consumo de APIs externas
* Tratamento e validação de dados
* Aplicação de regras de negócio
* Persistência organizada e reprocessável
* Preparação de dados para análise

---

## Problema de Negócio

Empresas que lidam com **atendimento ao público, operações, logística ou serviços** frequentemente precisam entender se **condições climáticas influenciam o volume de atendimentos ou a demanda**.

Algumas perguntas comuns nesse contexto:

* Dias mais quentes geram mais atendimentos?
* Chuvas impactam o comportamento do cliente?
* Existe correlação entre clima e volume operacional?

Para responder esse tipo de pergunta, é necessário **historizar dados climáticos confiáveis**, organizados por data, e disponíveis para análise temporal.

Este projeto resolve esse problema ao construir um **pipeline confiável e idempotente**, capaz de gerar um **dataset analítico limpo e consolidado**, pronto para cruzamento com dados de negócio.

---

## Arquitetura da Solução

### Tecnologias Utilizadas

* **Apache Airflow 2.8**
* **Python 3**
* **Pandas**
* **Docker e Docker Compose**
* **PostgreSQL** (metadados do Airflow)
* **API Open-Meteo** (dados climáticos históricos)

---

### Arquitetura de Dados (Data Lake em Camadas)

O pipeline segue uma arquitetura inspirada em **Data Lakes modernos**, organizada em três camadas:

```text
data/
├── raw/
│   └── climatedata/
│       └── YYYY-MM-DD.csv
├── processed/
│   └── climatedata/
│       └── YYYY-MM-DD.csv
└── analytics/
    └── climate_analytics.csv
```

#### Camada RAW

* Dados extraídos diretamente da API
* Sem aplicação de regras de negócio
* Particionados por data
* Garantem rastreabilidade e reprocessamento

#### Camada PROCESSED

* Dados validados e tratados
* Regras de negócio aplicadas
* Enriquecimento com metadados
* Mantêm particionamento por data

#### Camada ANALYTICS

* Dataset consolidado
* Ordenado temporalmente
* Pronto para análises, dashboards ou notebooks

---

## Orquestração com Apache Airflow

O pipeline é orquestrado por uma DAG chamada:

```text
climate_pipeline
```

### Configurações principais da DAG

* **Agendamento:** diário (`@daily`)
* **Start date:** `2026-01-01`
* **Catchup:** habilitado
* **Execução determinística por data**

Essa configuração permite:

* Processar dados históricos automaticamente
* Reprocessar qualquer data específica
* Garantir consistência temporal no pipeline

---

## Estrutura do Pipeline (Tasks)

### Extract – Extração de Dados Climáticos

**Responsabilidade:**

* Consumir a API Open-Meteo para uma data específica
* Extrair métricas climáticas diárias
* Persistir os dados brutos na camada RAW

**Características técnicas:**

* Uso da `execution_date (ds)` do Airflow
* Extração histórica via API `archive`
* Persistência particionada por data
* Retorno apenas do caminho do arquivo via XCom (boas práticas)

---

### Transform – Tratamento e Regras de Negócio

**Responsabilidade:**

* Ler dados da camada RAW
* Validar schema obrigatório
* Aplicar regras de negócio
* Persistir dados tratados na camada PROCESSED

**Principais regras aplicadas:**

* Validação de colunas obrigatórias
* Categorização da temperatura média:

  * `frio`
  * `ameno`
  * `quente`
* Inclusão de metadados de processamento (`processed_at`)

**Boas práticas adotadas:**

* Falha explícita em caso de inconsistência
* Uso de XCom apenas para metadados leves
* Separação clara entre dados brutos e tratados

---

### Load – Consolidação Analítica

**Responsabilidade:**

* Ler todos os arquivos da camada PROCESSED
* Consolidar os dados em um único dataset
* Ordenar cronologicamente
* Persistir o arquivo final na camada ANALYTICS

**Resultado:**

* Dataset único pronto para análise
* Ideal para uso em:

  * Pandas
  * Power BI
  * Notebooks analíticos
  * Modelagem estatística

---

## Infraestrutura com Docker

Todo o ambiente é executado via **Docker Compose**, garantindo:

* Reprodutibilidade
* Isolamento de dependências
* Setup simples
* Padronização do ambiente

Serviços utilizados:

* PostgreSQL (metadados do Airflow)
* Airflow Webserver
* Airflow Scheduler
* Airflow Init

---

## Persistência e Estratégia de Armazenamento

* Dados armazenados em **CSV**
* Particionamento por data (`YYYY-MM-DD`)
* Persistência via volumes Docker
* Simulação de padrões de Data Lake locais

**Benefícios dessa abordagem:**

* Idempotência
* Facilidade de reprocessamento
* Organização temporal clara
* Transparência e simplicidade

---

## Possibilidades de Análise

A camada `analytics` permite facilmente:

* Análise de tendências climáticas
* Correlação com indicadores operacionais
* Criação de dashboards
* Exploração em notebooks
* Estudos estatísticos

O projeto foi pensado para servir como **base para análises futuras**, sem necessidade de alterar o pipeline.

---

## O que este projeto demonstra

* Orquestração de pipelines com Airflow
* Consumo e tratamento de dados via API
* Arquitetura de dados em camadas
* Reprocessamento e idempotência
* Validação de dados
* Aplicação de regras de negócio
* Organização e clareza arquitetural

---

## Próximos Passos

* Análises exploratórias com a camada analytics
* Integração com Power BI
* Persistência em Parquet
* Escrita em banco de dados analítico
* Testes de qualidade de dados

---

## Autor

Projeto desenvolvido por **Carlos Jorge**, com foco em **Engenharia de Dados e Analytics Engineering**.