# Robust Secure Aggregation For Co-located IoT Devices With Corruption Localization.

This project provides simple, efficient secure aggregation for IoT devices. Two servers aid in the secure aggregation: an aggregating server, and a main decrypting server. Devices are co-located with other devices, forming groups of devices that should report the same value. 

Devices hide their values with a device-main-server-owned symmetric key. Encrypted values are sent to the aggregating server, who aggregates values and sends the results to the main server for decryption.

Assuming an honest majority in each group of devices, the presence of malicious or faulty devices, which report an incorrect value, is detected by the servers. This is done by comparing the obtained value with the one reported by the majority of devices. See paper for more info.


## Installation:

Prerequisites: OpenSSL, numpy

Clone this repository.

Testing with no corruptions:
```
  .\test-no-corrupt.sh n d
```
where n is the number of groups, and d is the number of devices per group. For instance:
```
  .\test-no-corrupt.sh 50 5
```

Testing with the maximum number of corruptions:
```
  .\test-max-corruption.sh n d
```
where n is the number of groups, and d is the number of devices per group. For instance:
```
  .\test-max-corruption.sh 50 5
```
