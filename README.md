[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/GetCon-Hungary/fmc-analyser)

# FMC Analyser

![FMC Analyser logo](assets/fmc_analyser_logo.png)

## Overview

FMC Analyser is a powerful tool designed to analyse access policies from Cisco Secure Firewall Management System. It facilitates security analysis and audits by providing detailed insights into access rules. With the ability to export to Excel and additional analytical features, FMC Analyser empowers users to assess network security comprehensively.

## Key Features

- **Access policy analysis**: Gain deep insights into access policies, enabling efficient security analysis and audit processes.

- **Export to Excel**: Seamlessly export analysis results to Excel for further review and sharing with stakeholders.

- **Comprehensive metrics**: Calculate various metrics including network objects and network group size, duplicates, references from ACP rules, group complexity and depth, port and port group size, reference count, duplicates, and security risk.

- **Customizable risk assessment**: Users can customize risk classes based on their specific security requirements, allowing for tailored risk assessment.

## How It Works

1. **Input access policies**: Import access policies from Cisco Secure Firewall Management System into FMC Analyser.

2. **Analytical calculations**: FMC Analyser calculates a range of metrics including network object sizes, duplicates, rule references, and security risk levels.

3. **Generate Excel report**: Generate a comprehensive Excel report containing calculated risk levels for all access rules. Rules posing high security risks, such as those allowing broad source IPs like 'any', are highlighted for immediate attention.

4. **Customize risk parameters**: Users have the flexibility to adjust risk parameters to align with their organization's security policies and priorities.

## Getting Started

1. Clone the FMC Analyser repository from GitHub: `git clone https://github.com/GetCon-Hungary/fmc-analyser.git`

2. Install the necessary dependencies specified in the `requirements.txt` file: `pip install -r requirements.txt`

3. Customize risk parameters, if needed in the `config.yml` file.

4. Run FMC Analyser to start the processing (See [Usage examples](#usage-examples))

5. Analyse the generated Excel report to identify security risks and take necessary actions.

## Usage

- First configure the application to your needs by modifying the `config.yml` file.
- Run the application with the following: `python3 analyser.py`
- Command line arguments
  - `-H / --host`: IP address of FMC (required)
  - `-U / --username`: FMC login username (required)
  - `-P / --password`: FMC login password (required)
  - `-A / --acp`: Rule name you want to analyse. Leave blank for default "all"
  - `-C / --config`: Config file path. Leave blank for default: `config.yml`

### Usage examples

- Run with default settings:

```bash
python3 analyser.py \
  --host 10.10.10.1
  --username administrator
  --password administrator!
```

- Run with custom parameters:

```bash
python3 analyser.py \
  --host 10.10.10.1
  --username administrator
  --password administrator!
  --acp Sample_policy
  --config my_conf.yml
```

- Run by functions:

```python
# Import FMC Analyser module
import fmc_analyser

# Load access policies from Cisco Secure Firewall Management System
fmcloader = logic.fmc_loader.FMCLoader(fmc_host='10.10.10.1', username='superman', password='not_batman123', acp_name='gotham_sec')

# Build up the data models
builder = logic.builder_logic.Builder(fmcloader)

# Parse FMC data into easy-to-use formats
data = logic.export_data_logic.Data(builder, config='my_conf.yml')

# Generate Excel report for access policies
logic.excel_export(data.access_policies_data, exp.ACCESS_POLICY_HEADER, 'access_policies_information')
```

## Support

For any questions or issues, please contact our support team at <devnet@getcon.hu>.

## License

This project is licensed under the GNU General Public License version 3.0 - see the LICENSE file for details.

## Acknowledgments

- [fmcapi](https://github.com/marksull/fmcapi)

## Contributors

- Balázs Farkas (@gc-farkasb)
- Egon Gombár (@Egonka2000)
- Norbert Omodi
- Barnabás Kerekes (@kerekesb)
- Botond Barta
- Péter Rostás

---

Thank you for choosing FMC Analyser for your security analysis needs. We're committed to continually improving our tool to help you better secure your network infrastructure.
