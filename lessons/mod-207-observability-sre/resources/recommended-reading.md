# Module 207: Recommended Reading and Resources

## Books

### SRE Fundamentals
1. **Site Reliability Engineering: How Google Runs Production Systems**
   - Authors: Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy
   - Publisher: O'Reilly Media (2016)
   - Why: The foundational text on SRE principles
   - Key Chapters: 4 (Service Level Objectives), 6 (Monitoring Distributed Systems), 11 (Being On-Call)

2. **The Site Reliability Workbook**
   - Authors: Betsy Beyer, Niall Richard Murphy, David K. Rensin, Kent Kawahara, Stephen Thorne
   - Publisher: O'Reilly Media (2018)
   - Why: Practical implementation guidance for SRE
   - Key Chapters: 2 (Implementing SLOs), 15 (Postmortem Culture)

3. **Seeking SRE**
   - Authors: David N. Blank-Edelman (Editor)
   - Publisher: O'Reilly Media (2018)
   - Why: Diverse perspectives on implementing SRE
   - Key Chapters: Varies by topic

### Observability
4. **Observability Engineering**
   - Authors: Charity Majors, Liz Fong-Jones, George Miranda
   - Publisher: O'Reilly Media (2022)
   - Why: Modern observability practices and philosophy
   - Focus: High-cardinality data, distributed systems, debugging production

5. **Distributed Tracing in Practice**
   - Authors: Austin Parker, Daniel Spoonhower, Jonathan Mace, Ben Sigelman, Rebecca Isaacs
   - Publisher: O'Reilly Media (2020)
   - Why: Comprehensive guide to distributed tracing
   - Key Topics: OpenTelemetry, instrumentation strategies, trace analysis

6. **Logging and Log Management**
   - Authors: Anton Chuvakin, Kevin Schmidt, Chris Phillips
   - Publisher: Syngress (2012)
   - Why: Comprehensive logging strategies (though dated, principles remain valid)

### Chaos Engineering
7. **Chaos Engineering: System Resiliency in Practice**
   - Authors: Casey Rosenthal, Nora Jones
   - Publisher: O'Reilly Media (2020)
   - Why: The definitive guide to chaos engineering
   - Key Concepts: Principles of chaos, designing experiments, organizational adoption

8. **Learning Chaos Engineering**
   - Author: Russ Miles
   - Publisher: O'Reilly Media (2019)
   - Why: Hands-on approach to chaos engineering

### Monitoring and Alerting
9. **Practical Monitoring**
   - Author: Mike Julian
   - Publisher: O'Reilly Media (2017)
   - Why: Effective monitoring strategies
   - Key Topics: Anti-patterns, building better alerts

10. **Prometheus: Up & Running**
    - Authors: Brian Brazil
    - Publisher: O'Reilly Media (2018)
    - Why: Comprehensive Prometheus guide by a core developer
    - Key Chapters: Advanced querying, federation, long-term storage

### Machine Learning Operations
11. **Machine Learning Design Patterns**
    - Authors: Valliappa Lakshmanan, Sara Robinson, Michael Munn
    - Publisher: O'Reilly Media (2020)
    - Relevant Chapters: Model monitoring, serving patterns
    - Why: ML-specific patterns including observability

12. **Designing Data-Intensive Applications**
    - Author: Martin Kleppmann
    - Publisher: O'Reilly Media (2017)
    - Why: Understanding distributed systems that support ML
    - Relevant Chapters: Monitoring, reliability

## Research Papers

### ML Monitoring and Observability
1. **Hidden Technical Debt in Machine Learning Systems**
   - Authors: Sculley et al. (Google)
   - Published: NIPS 2015
   - Link: https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html
   - Key Insight: ML systems accumulate unique technical debt, including monitoring debt

2. **Machine Learning: The High-Interest Credit Card of Technical Debt**
   - Authors: Sculley et al. (Google)
   - Published: SE4ML Workshop, NIPS 2014
   - Why: Identifies monitoring challenges specific to ML systems

3. **Continuous Training for Production ML in the TensorFlow Extended (TFX) Platform**
   - Authors: Baylor et al. (Google)
   - Published: KDD 2019
   - Relevant Sections: Model validation, monitoring pipelines

### Distributed Tracing
4. **Dapper, a Large-Scale Distributed Systems Tracing Infrastructure**
   - Authors: Sigelman et al. (Google)
   - Published: Google Technical Report (2010)
   - Link: https://research.google/pubs/pub36356/
   - Why: The foundational distributed tracing paper

### Chaos Engineering
5. **Principles of Chaos Engineering**
   - Source: principlesofchaos.org
   - Why: Defines the core principles

## Online Courses and Certifications

### SRE and Reliability
1. **Google Cloud Professional Cloud Architect**
   - Provider: Google Cloud
   - Link: https://cloud.google.com/certification/cloud-architect
   - Relevant Topics: Reliability engineering, monitoring

2. **Site Reliability Engineering: Measuring and Managing Reliability**
   - Provider: Google (Coursera)
   - Link: https://www.coursera.org/learn/site-reliability-engineering-slos
   - Topics: SLIs, SLOs, error budgets

### Observability
3. **Observability in Cloud Native Apps**
   - Provider: Linux Foundation (edX)
   - Topics: Prometheus, Jaeger, OpenTelemetry

4. **DataDog Fundamentals**
   - Provider: DataDog
   - Link: https://learn.datadoghq.com/
   - Why: Hands-on with enterprise observability platform

### Prometheus and Grafana
5. **Prometheus & Grafana**
   - Provider: Udemy, A Cloud Guru
   - Topics: Setup, configuration, advanced queries

### Chaos Engineering
6. **Chaos Engineering on Kubernetes**
   - Provider: Various (Udemy, Pluralsight)
   - Topics: Chaos Mesh, Litmus

## Documentation and Official Guides

### Prometheus Ecosystem
1. **Prometheus Documentation**
   - Link: https://prometheus.io/docs/
   - Key Sections: Best practices, federation, storage

2. **Thanos Documentation**
   - Link: https://thanos.io/
   - Topics: Architecture, deployment, troubleshooting

3. **Grafana Documentation**
   - Link: https://grafana.com/docs/
   - Focus: Dashboards, alerting, data sources

### Tracing
4. **OpenTelemetry Documentation**
   - Link: https://opentelemetry.io/docs/
   - Why: Industry standard for observability

5. **Jaeger Documentation**
   - Link: https://www.jaegertracing.io/docs/
   - Topics: Architecture, deployment, sampling

### Logging
6. **Elasticsearch Guide**
   - Link: https://www.elastic.co/guide/index.html
   - Key Sections: Index lifecycle, search, aggregations

7. **Loki Documentation**
   - Link: https://grafana.com/docs/loki/
   - Why: Cost-effective logging for Kubernetes

### Chaos Engineering
8. **Chaos Mesh Documentation**
   - Link: https://chaos-mesh.org/docs/
   - Topics: Chaos experiments, Kubernetes integration

9. **Litmus Documentation**
   - Link: https://litsuschaos.io/
   - Topics: Chaos workflows, experiments catalog

## Blogs and Online Resources

### SRE and Observability
1. **Google SRE Book Online**
   - Link: https://sre.google/books/
   - Why: Free access to Google's SRE books

2. **Honeycomb Blog**
   - Link: https://www.honeycomb.io/blog
   - Focus: Observability best practices, high-cardinality data

3. **SRE Weekly Newsletter**
   - Link: https://sreweekly.com/
   - Why: Weekly curated SRE content

### Prometheus and Monitoring
4. **Robust Perception Blog**
   - Link: https://www.robustperception.io/blog
   - Author: Brian Brazil (Prometheus core developer)
   - Topics: Advanced Prometheus techniques

5. **Prometheus Community**
   - Link: https://prometheus.io/community/
   - Forums, Slack, mailing lists

### Chaos Engineering
6. **Chaos Engineering Blog (Gremlin)**
   - Link: https://www.gremlin.com/blog/
   - Topics: Chaos experiments, case studies

7. **Netflix Tech Blog**
   - Link: https://netflixtechblog.com/tagged/chaos-engineering
   - Why: Pioneers of chaos engineering

### ML Observability
8. **Evidently AI Blog**
   - Link: https://www.evidentlyai.com/blog
   - Topics: ML monitoring, drift detection

9. **WhyLabs Blog**
   - Link: https://whylabs.ai/blog
   - Topics: Data quality, ML observability

## Conference Talks and Videos

### SREcon
1. **SREcon Conferences**
   - Link: https://www.usenix.org/conferences/byname/925
   - Why: Premier SRE conference with recorded talks

### KubeCon
2. **KubeCon + CloudNativeCon**
   - Link: https://www.cncf.io/kubecon-cloudnativecon-events/
   - Topics: Observability, chaos engineering in Kubernetes

### ObservabilityCON
3. **Grafana ObservabilityCON**
   - Link: https://grafana.com/about/events/observabilitycon/
   - Topics: Grafana, Prometheus, Loki, Tempo

## Podcasts

1. **Command Line Heroes (Red Hat)**
   - Episodes on SRE and DevOps
   - Link: https://www.redhat.com/en/command-line-heroes

2. **SRE Path**
   - Link: https://srepath.com/
   - Focus: SRE interviews and discussions

3. **On-Call Nightmares Podcast**
   - Link: https://www.pagerduty.com/podcast/
   - Why: Real incident stories

## Community and Forums

1. **CNCF Slack**
   - Channels: #prometheus, #jaeger, #opentelemetry
   - Link: https://slack.cncf.io/

2. **SRE Subreddit**
   - Link: https://www.reddit.com/r/SRE/
   - Why: Community discussions

3. **Prometheus Users Google Group**
   - Link: https://groups.google.com/g/prometheus-users

## Tools and Platforms to Explore

### Open Source
1. **Grafana Labs OSS**
   - Grafana, Loki, Tempo, Mimir
   - Try: Local deployment, playground

2. **OpenTelemetry Demo**
   - Link: https://opentelemetry.io/docs/demo/
   - Why: Hands-on with distributed tracing

### Enterprise (Trial Accounts)
1. **DataDog**
   - 14-day free trial
   - Link: https://www.datadoghq.com/

2. **New Relic**
   - Free tier available
   - Link: https://newrelic.com/

3. **Splunk**
   - Free tier for small deployments
   - Link: https://www.splunk.com/

## Practice Environments

1. **Katacoda / Killercoda**
   - Interactive scenarios for Kubernetes, Prometheus
   - Link: https://killercoda.com/

2. **Play with Kubernetes**
   - Link: https://labs.play-with-k8s.com/
   - Why: Free Kubernetes environment

3. **Instruqt**
   - Link: https://instruqt.com/
   - Interactive labs for various tools

## GitHub Repositories

1. **Awesome SRE**
   - Link: https://github.com/dastergon/awesome-sre
   - Why: Curated list of SRE resources

2. **Awesome Chaos Engineering**
   - Link: https://github.com/dastergon/awesome-chaos-engineering

3. **Awesome Prometheus**
   - Link: https://github.com/roaldnefs/awesome-prometheus

4. **OpenTelemetry Examples**
   - Link: https://github.com/open-telemetry/opentelemetry-demo

## Recommended Learning Path

### Beginner
1. Start with Google SRE Book (Chapters 1-4)
2. Prometheus: Up & Running
3. Complete Prometheus online course
4. Practice with local Prometheus setup

### Intermediate
5. The Site Reliability Workbook
6. Distributed Tracing in Practice
7. Implement OpenTelemetry in a sample app
8. Deploy Jaeger and analyze traces

### Advanced
9. Observability Engineering
10. Chaos Engineering book
11. Conduct chaos experiments
12. Read ML monitoring papers
13. Implement comprehensive ML observability

## Staying Current

1. **Subscribe to newsletters**: SRE Weekly, Observability News
2. **Follow thought leaders**: Charity Majors, Liz Fong-Jones, Niall Murphy on Twitter/LinkedIn
3. **Attend conferences**: SREcon, KubeCon (virtual attendance available)
4. **Join communities**: CNCF Slack, SRE Slack communities
5. **Read release notes**: Prometheus, OpenTelemetry, Grafana
6. **Experiment continuously**: Deploy latest versions, try new features

---

**Last Updated**: 2025-10-16
**Module**: 207 - Advanced Observability and SRE Practices
