# FMC analyser

![FMC Analyser logo](assets/fmc_analyser_logo.png)

## Introduction

FMCAnalyser can download, export and analyse wide range of data from Cisco Secure Firewall Management Center (FMC). The scope of the project is to process most of the production data in FMC, with support for the latest version.

## Features

- Parse FMC objects into Excel table.
- Extra analyses of exported data:
  - Duplicates for networks, ports and port groups.
  - Size of networks.
  - Riskyness of ports.
  - Depth of nested network groups.

## Support

- Tested on FMC 7.2.5 (build 208)
- IPv4 only
- Supported FMC data:
  - Hosts
  - Networks
  - Network groups
  - Ranges
  - Ports
  - Port groups
  - Access rules
  - Access policies

## Getting Started

### Requirements

- Python >= 3.9
- Python libraries outlined in `requirements.txt`

### Usage

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

## Acknowledgments

- [fmcapi](https://github.com/marksull/fmcapi)
