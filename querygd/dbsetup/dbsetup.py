#!/usr/bin/env python3

import csv
import logging
import os
import time
from textwrap import dedent

import psycopg2


def main() -> None:
    """Main method used for delegating the database setup.

    Encapsulates:
    - creation of a single table
    - population of the table from the TSV-format VCF file as the source
    - creation of two indexes, one of which is a multicolumn index (CHROM, POS) while the other is single (ID)
    """
    logging.basicConfig(level=logging.INFO)

    conn = None  # Avoid potential references before assignment

    try:
        conn = establish_connection()

        create_table(conn)
        populate_table(conn)
        create_indexes(conn)

    except (psycopg2.DatabaseError, Exception) as exc:
        logging.error(exc)

    finally:
        if conn is not None:
            conn.close()
            logging.info('Database connection closed')

    logging.info('Complete, stopping the initial setup process...')


def establish_connection():
    """Establishes a connection to the database."""

    logging.info('Establishing database connection...')

    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )


def create_table(conn) -> None:
    """Creates a table of a simplified VCF format, omitting a few standard columns."""

    create_table_command: str = dedent(
        '''
        CREATE TABLE genedata (
            CHROM VARCHAR(255) NOT NULL,
            POS VARCHAR(255) NOT NULL,
            ID VARCHAR(255) NOT NULL,
            REF VARCHAR(255) NOT NULL,
            ALT VARCHAR(255) NOT NULL,
            FORMAT VARCHAR(255) NOT NULL
        );
        '''
    ).strip()

    logging.info('Creating table... (1/2)')

    with conn.cursor() as cur:
        cur.execute(create_table_command)

    conn.commit()

    logging.info('Created table (2/2)')


def populate_table(conn) -> None:
    """Populates the created table via a passed TSV-format VCF file as the source.

    Path to the VCF file is read from the VCF_FILE_PATH environment variable.
    Commits the insert changes every 1000 rows to lower commit overhead.
    """
    populate_table_command: str = dedent(
        '''
        INSERT INTO genedata (CHROM, POS, ID, REF, ALT, FORMAT)
        VALUES (%s, %s, %s, %s, %s, %s);
        '''
    ).strip()

    logging.info('Populating table, this might take a while if there are a lot of rows... (1/2)')

    with open(os.getenv('VCF_FILE_PATH'), 'r') as rf:
        for idx, line in enumerate(csv.reader(rf, delimiter='\t')):

            if line[0].startswith('#'):
                continue

            line: list = [unit.strip() for unit in line]

            with conn.cursor() as cur:
                cur.execute(populate_table_command, tuple(line))

            if idx % 1000 == 0:
                conn.commit()

        conn.commit()

    logging.info('Populated table (2/2)')


def create_indexes(conn) -> None:
    """Creates two indexes, a multicolumn index (CHROM, POS) and a single one (ID).

    Both indexes utilize the default binary root (b-tree) access method.
    """
    create_index_command: str = 'CREATE INDEX idx_rsid ON genedata(id);'
    create_mult_index_command: str = 'CREATE INDEX mult_idx_chrom_pos ON genedata(chrom, pos);'

    logging.info('Creating indexes... (1/2)')

    with conn.cursor() as cur:
        cur.execute(create_index_command)
        cur.execute(create_mult_index_command)

    conn.commit()

    logging.info('Created indexes (2/2)')


if __name__ == '__main__':
    time.sleep(int(os.getenv('DB_WAIT_TIME')))  # Await the database to be ready
    main()
