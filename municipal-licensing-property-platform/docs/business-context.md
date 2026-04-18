# Business Context Notes

This implementation assumes a municipal environment similar to Maharashtra ULBs where:

- property data, licensing workflows, GIS, and finance may already exist in multiple systems,
- a workflow platform must coexist with legacy ERP and GIS tools rather than replace everything at once,
- Marathi and English user experience may both be required,
- auditability, digital evidence, and controlled role-based approvals are mandatory.

## C-DAC relevance

C-DAC is relevant in this domain as a potential technology partner rather than as the only possible full-stack municipal asset product. In practice, municipalities may integrate with or evaluate:

- **C-DAC NextGen ERP** for administrative, finance, procurement, HR, and workflow-heavy enterprise functions,
- **C-DAC WAMIS** for public infrastructure, works, and accounts style project/financial management,
- **e-Pramaan** if a government-standard authentication plane is mandated,
- **e-Hastakshar** where legally valid digital signing is needed,
- **GIST / language technologies** for multilingual interfaces.

This repository therefore treats ERP, works, GIS, and signature systems as external integration points and focuses on a resilient local workflow core.
