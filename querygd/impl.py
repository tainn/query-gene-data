import logging
import os
from textwrap import dedent
from typing import Optional

import psycopg2

from models import GeneSequence


async def get_data(q: str) -> GeneSequence:
    """Main method used for delegating the implementation of handling the GET request to the /data endpoint.

    Encapsulates:
    - appropriate query selection and execution based on the received data string
    - build of a GeneSequence object response after fetching a single-row result
    """
    logging.basicConfig(level=logging.INFO)

    # Avoid potential references before assignment
    conn = None
    result = None

    try:
        conn = establish_connection()

        result: Optional[list] = select(conn, q)

    except (psycopg2.DatabaseError, Exception) as exc:
        logging.error(exc)

    finally:
        if conn is not None:
            conn.close()
            logging.debug('Database connection closed')

    logging.debug('Sending response...')

    return GeneSequence(*result) if result is not None else GeneSequence()


def establish_connection():
    """Establishes a connection to the database."""

    logging.debug('Establishing database connection...')

    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )


def select(conn, q: str) -> Optional[list]:
    """Selects and executes the appropriate query based on the received data string.

    Queries:
    - if there are no spaces in the string, it queries for the ID column
    - if there is one valid space in the string, it queries for the CHROM and POS columns

    In case an invalid query is passed or the database does not return any rows, None is returned.
    """
    if ' ' not in q:
        select_command: str = dedent(
            '''
            SELECT * FROM genedata
            WHERE ID = %s;
            '''
        ).strip()

        with conn.cursor() as cur:
            cur.execute(select_command, (q,))
            result: Optional[list] = cur.fetchone()

        logging.debug('WHERE statement applied on the ID column')

    elif len(q.split()) == 2:
        select_command: str = dedent(
            '''
            SELECT * FROM genedata
            WHERE CHROM = %s and POS = %s;
            '''
        ).strip()

        chrom, pos = q.split()

        with conn.cursor() as cur:
            cur.execute(select_command, (chrom, pos))
            result: Optional[list] = cur.fetchone()

        logging.debug('WHERE statement applied on the CHROM and POS columns')

    else:
        result = None

        logging.error('More than two parameters passed, no query performed')

    if result is None:
        logging.error(f'No rows successfully selected from the query')

    conn.commit()

    return result
