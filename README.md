# Public Sector Workflows & Prototypes

**Repository of Personal Automation Tools for Public Sector & NatSec Contexts**

This repository serves as a **portfolio archive** to demonstrate my technical background and problem-solving approach as an Engagement Manager / Project Manager.

> **⚠️ Context & Disclaimer:**
> * **Timeframe:** The codes in this repository were originally created around **2022-2023**.
> * **Purpose:** They are archived here to demonstrate my "Builder's Mindset"—the ability to prototype independent solutions for administrative challenges.
> * **Status:** As these are legacy scripts ("Works on my machine" era), dependencies may be outdated. They are presented primarily to showcase logic and architectural thinking rather than production-readiness.

---

## Project 1: Ministry of Internal Affairs News Monitor (Serverless)
**File:** `gov_news_monitor.py`

### Overview
各省庁（総務省、経産省など）の報道発表を24時間監視し、特定のキーワード（安保、通信インフラ等）を含む重要情報をリアルタイムで検知・LINE通知する **Serverless Intelligence System**。

### Why I built this
コンサルタントとして多忙を極める中、「毎日決まった時間に各省庁のサイトを見に行く」というルーチンを維持することは困難であり、数日分の確認漏れが発生するリスクがありました。
そこで、**「人間が情報を取りに行く（Pull）」のではなく、「システムが情報を届ける（Push）」仕組み**に変えることで、情報収集という"習慣"そのものをコードにアウトソースしました。

### Core Value
* **Eliminating Manual Dependency:** 人間の記憶や意志力に依存したチェック体制を廃止し、システムによる定期実行で信頼性を担保。
* **Push over Pull:** サイト巡回の負荷をゼロにし、通知が来たときだけ確認すればよい状態（Event-driven）を確立。
* **Consistent Monitoring:** 繁忙期や休暇中であっても、システムの監視が止まることはなく、情報の連続性を維持。

### Architecture (Legacy)
* **Compute:** Google Cloud Functions (Python 3.x)
* **Storage:** Google Cloud Storage (State management for diff detection)
* **Notification:** LINE Notify API
* **Logic:** Web Scraping & Anti-join (Diff detection)

### 💡 Lessons Learned & Modern Re-design
運用を通じて、「全件通知ではノイズが多い」「チーム共有がしにくい」という課題が見えてきました。現在、最新のクラウド技術（AWS/Azure）を用いて再設計するなら、以下のアーキテクチャを採用します。

1.  **Intelligent Filtering with GenAI:**
    * 単なるキーワードマッチではなく、**Generative AI (e.g., Azure OpenAI Service / Amazon Bedrock)** を組み込み、記事内容を要約および「安保上の重要度」を判定させることで、ノイズを削減する。
2.  **Enterprise Collaboration:**
    * 個人のLINEではなく、**Enterprise Tools (e.g., Microsoft Teams / Slack)** へ通知先を変更し、組織全体での情報共有とリアクションを可能にする。
3.  **Infrastructure as Code (IaC):**
    * 手動デプロイではなく、**Terraform / AWS CDK / Bicep** を用いてインフラをコード管理し、再現性を担保する。

---

## Project 2: Demographic Trend Analysis & Visualization (GIS)
**File:** `population_gis_analysis.py`

### Overview
500mメッシュ別将来推計人口データ（シェープファイル）を解析し、2015年から2050年にかけた「人口減少率」を算出・可視化する **Geospatial Analytics Tool**。
どの地域が消滅可能性が高いか（Red Zone）をヒートマップとして即座に可視化します。

### Why I built this
自治体やインフラ企業のコンサルティングにおいて、人口減少は避けて通れない課題ですが、単なる「数字の羅列（Excel表）」では危機感が直感的に伝わりません。
また、従来のデスクトップGISソフトでの手作業による色塗りは、再現性が低く時間がかかります。
そこで、**「データさえ入れ替えれば、即座に政策判断に必要な地図が出力される」パイプライン**を構築し、意思決定のスピードを上げるために開発しました。

### Core Value
* **Data-Driven Policy Making:** 「なんとなく人が減っている」という定性的な感覚を、「減少率80%以上のエリア」として定量的に定義・可視化。
* **Reproducibility:** パラメータ（閾値）を変えるだけで、異なるシナリオ（楽観/悲観）の分析マップを瞬時に再生成可能。
* **Effective Communication:** 専門知識がないステークホルダー（首長や住民）に対しても、一目で課題が伝わる視覚的根拠を提供。

### Architecture (Legacy)
* **Language:** Python 3.x
* **Libraries:** `Geopandas`, `Shapely`, `Matplotlib`
* **Input:** 500m Mesh Shapefile (Open Data)

### 💡 Lessons Learned & Modern Re-design
ローカルPCでの処理では「全国規模のデータ処理に時間がかかる」「静的な画像でしか対話できない」という限界がありました。クラウドネイティブなデータ基盤として再構築するなら、以下のアプローチをとります。

1.  **Scalable Data Lake:**
    * シェープファイルやCSVをオブジェクトストレージ (**Amazon S3 / Azure Blob Storage**) に格納し、サーバーレスなクエリエンジン (**Amazon Athena / Azure Synapse Analytics**) で必要なエリア・属性を抽出する。
2.  **Interactive BI Dashboard:**
    * 静的な画像出力（Matplotlib）ではなく、**Amazon QuickSight / Microsoft Power BI** の地理空間機能を用い、ユーザーがズームやフィルタリングできる対話型ダッシュボードへ進化させる。
3.  **Automated ETL Pipelines:**
    * データの更新に合わせて自動的に分析マートを作成するため、**AWS Glue / Azure Data Factory** によるETL処理を実装する。
