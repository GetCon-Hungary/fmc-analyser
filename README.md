# FMC analyser

## Introduction

FMCAnalyser can download, parse and export a wide range of data from Cisco Secure Firewall Management Center (FMC) including analyses of the data.

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

- Python >= 3.6
- Python libraries outlined in `requirements.txt`

### Usage

- First configure the application to your needs by modifying the `config.yaml` file.
- Run the application with the following: `python3 main.py`

## Contributing

Please use the issue tracker to report any bugs or file feature requests.

## Acknowledgments

- [fmcapi](https://github.com/marksull/fmcapi)
