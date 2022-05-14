# query-gene-data

A service that accepts `GET` requests on the `/data` endpoint with a query string `q` and returns the corresponding gene
sequence variation values from the database.

## Run

The included docker-compose file declares three services:

- `query-gene-data`: the core service
- `postgres-db`: the postgres database
- `db-init-setup`: the service which initially sets the database up

Due to all three generally being required, running is achieved from an encapsulating up command:

```
docker-compose up
```

## Config

Configurable segments are primarily passed in as environment variables, set under the `environment` nodes of the
docker-compose file.

An example of such a config is the `VCF_FILE_PATH` variable under the `db-init-setup` service which specifies the path
to the VCF file that we want to parse and populate the database with. Inside the `querygd/dbsetup` directory, there
already exists a pre-included sample VCF file `hg37_1k_lines.vcf`.

As per its name, it includes the first one thousand (1k) rows of the original VCF file. If passing other, potentially
larger files, the value of this env var has to be changed correspondingly.

## Logs

Explicit logging is present on the `db-init-setup` and `query-gene-data` services. Initially, most of the logs of the
former are set to `INFO` and the latter to `DEBUG`, as the former's one-time process is crucial.

Specifically, before continuing with queries or similar activity, the following log should be output, which denotes a
successful initial setup completion:

```
INFO:root:Complete, stopping the initial setup process...
```

The larger the VCF file that we want to populate the database with is, the longer this process will generally take. In
such a scenario, the temporarily last output log will be the following:

```
INFO:root:Populating table, this might take a while if there are a lot of rows... (1/2)
```

## Request

`GET` requests are accepted on a `/data` endpoint. A query string is passed under the `q` key. By default, the service
is exposed on port `8000`.

Example request on a local endpoint...

```
http://localhost:8000/data?q=rs536526699
```

... results in the following response:

```json
{
  "chrom": "1",
  "pos": "135095",
  "id": "rs536526699",
  "ref": "C",
  "alt": "T",
  "format": "AF=2.56329e-05;INFO=0;RAF=0.000199681"
}
```
