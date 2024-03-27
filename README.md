# FMC analyser

![FMC Analyser logo](assets/fmc_analyser_logo.png)
# FMC Analyser

![FMC Analyser logo](assets/fmc_analyser_logo.png)

## Overview

FMCAnalyser can download, export and analyse wide range of data from Cisco Secure Firewall Management Center (FMC). The scope of the project is to process most of the production data in FMC, with support for the latest version.
FMC Analyser is a powerful tool designed to analyze Access Policies from Cisco Secure Firewall Management System. It facilitates security analysis and audits by providing detailed insights into access rules. With the ability to export to Excel and additional analytical features, FMC Analyser empowers users to assess network security comprehensively.

## Key Features

- **Access Policy Analysis**: Gain deep insights into access policies, enabling efficient security analysis and audit processes.
  
- **Export to Excel**: Seamlessly export analysis results to Excel for further review and sharing with stakeholders.

- **Comprehensive Metrics**: Calculate various metrics including network objects and network group size, duplicates, references from ACP rules, group complexity and depth, port and port group size, reference count, duplicates, and security risk.

- **Customizable Risk Assessment**: Users can customize risk classes based on their specific security requirements, allowing for tailored risk assessment.

## How It Works

1. **Input Access Policies**: Import Access Policies from Cisco Secure Firewall Management System into FMC Analyser.

2. **Analytical Calculations**: FMC Analyser calculates a range of metrics including network object sizes, duplicates, rule references, and security risk levels.

3. **Generate Excel Report**: Generate a comprehensive Excel report containing calculated risk levels for all access rules. Rules posing high security risks, such as those allowing broad source IPs like 'any', are highlighted for immediate attention.

4. **Customize Risk Parameters**: Users have the flexibility to adjust risk parameters to align with their organization's security policies and priorities.

## Getting Started

### Requirements

- Python >= 3.9
- Python libraries outlined in `requirements.txt`

### Usage
1. Clone the FMC Analyser repository from GitHub.

2. Install the necessary dependencies specified in the requirements.txt file.

3. Run FMC Analyser and import Access Policies from Cisco Secure Firewall Management System.

4. Customize risk parameters if needed.

5. Analyze the generated Excel report to identify security risks and take necessary actions.

## Usage 

- First configure the application to your needs by modifying the `config.yml` file.
- First configure the application to your needs by modifying the `config.yml` file.
- Run the application with the following: `python3 main.py`
- Command line arguments
  - `-h / --host`: IP address of FMC (required)
  - `-u / --username`: FMC login username (required)
  - `-p / --password`: FMC login password (required)
  - `-a / --acp`: Choose from the following or leave blank for default "all": acp, ports, networks
  - `-c / --config`: Enter configuration file path. If skipped, the default is used: `config.yml`

### Example

- If you want to set custom parameters:

```bash
python3 main.py \
  --host 10.10.10.1
  --username administrator
  --password administrator!
  --acp networks
  --config my_conf.yml
```

- If you want to leave most things on default:

```bash
python3 main.py \
  --host 10.10.10.1
  --username administrator
  --password administrator!
```

## Contributing

Please use the issue tracker to report any bugs or file feature requests.
  - `-h / --host`: IP address of FMC (required)
  - `-u / --username`: FMC login username (required)
  - `-p / --password`: FMC login password (required)
  - `-a / --acp`: Choose from the following or leave blank for default "all": acp, ports, networks
  - `-c / --config`: Enter configuration file path. If skipped, the default is used: `config.yml`

### Example

- Run with default settings:

```bash
python3 main.py \
  --host 10.10.10.1
  --username administrator
  --password administrator!
```

- Run with custom parameters:

```bash
python3 main.py \
  --host 10.10.10.1
  --username administrator
  --password administrator!
  --acp Sample_policy
  --config my_conf.yml
```

## Support

For any questions or issues, please contact our support team at support@fmc-analyser.com.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [fmcapi](https://github.com/marksull/fmcapi)

## Contributors

John Doe (@johndoe)

Jane Smith (@janesmith)

Thank you for choosing FMC Analyser for your security analysis needs. We're committed to continuously improving our tool to help you better secure your network infrastructure.
