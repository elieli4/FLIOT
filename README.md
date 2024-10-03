Robust Secure Aggregation For Co-located IoT Devices With Corruption Localization

Prerequisites: OpenSSL, numpy

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
