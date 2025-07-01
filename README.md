# Phase Defect Analysis (temporary title)

This repository contains the full pipeline for a study on **phase defects**, including:

- Python scripts to run and analyze simulations
- Python scripts to create the figures that are used in the paper
- LaTeX source code for the accompanying scientific paper

## Project Structure

📁 simulation/ Scripts to run simulations of phase defects
📁 analysis/ Scripts to post-process and analyze the simulation results
📁 snapshots/ Scripts to generate annotated figures and visualizations
📁 paper/ LaTeX source code for the paper
📁 data/ Empty by default; data is fetched from Zenodo

## Getting Started

Clone the repository and install the required Python dependencies:

```bash
git clone https://github.com/your-username/phase-defect-analysis.git
cd phase-defect-analysis
python3 -m venv venv
pip install -r requirements.txt
```

To reproduce the figures and analysis:

1. Run the simulation or use the archived data.
2. Use the analysis and snapshot scripts to generate plots and figures.
3. Compile the paper using `latexmk` or your preferred LaTeX workflow.

## Data Availability

All simulation outputs, and final figures are archived and publicly available via Zenodo:

👉 [**Zenodo Archive**](https://doi.org/xx.xxxx/zenodo.xxxxxx)

The Zenodo record includes:

- Raw simulation data
- Snapshots used in the manuscript
- A frozen version of this GitHub repository

## Preregistration and Clinical Relevance

Although this project is primarily theoretical, it is designed with **clinical applications in mind**.
The tools developed here support the design and setup of clinical studies involving phase defects.
To promote **transparency, reproducibility, and reusability**,
we have preregistered both the analysis tools and a clinical study protocol.

**Preregistration on OSF**:
The full preregistration, including the study rationale, expected outcomes, and intended analysis pipeline, is available at:

👉 [**OSF Project Page**](https://osf.io/your-project-id)

This registration includes:

- A formal study protocol for potential clinical implementation
- Documentation of simulation and analysis tools
- Planned hypotheses and outcome measures for clinical data

We encourage researchers and clinicians to reuse and adapt these tools for their own studies,
and we welcome collaboration or feedback.

## Citation

If you use this code or data, please cite the Zenodo archive:

```
@software{verstraeten2025,
  author       = {Bjorn Verstraeten},
  title        = {Phase Defect Analysis},
  year         = 2025,
  publisher    = {Zenodo},
  doi          = {10.xxxx/zenodo.xxxxxx},
  url          = {https://doi.org/10.xxxx/zenodo.xxxxxx}
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact Information

For questions, feedback, or collaboration inquiries, please contact:

### Lead Researcher

**Bjorn Verstraeten**  
PhD Researcher, Ghent University  
📧 bjorn.verstraeten@ugent.be

### Supervisor

**Nele Vandersickel**  
Professor, Ghent University  
📧 nele.vandersickel@ugent.be
