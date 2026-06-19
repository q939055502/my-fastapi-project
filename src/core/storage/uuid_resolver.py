import uuid as uuid_module

from sqlalchemy import text

from src.core.log import logger
from src.core.storage.cache import cache_manager


def _is_valid_uuid(uuid_str: str) -> bool:
    try:
        uuid_module.UUID(uuid_str)
        return True
    except ValueError:
        return False


class UuidResolver:
    def resolve(
        self,
        session,
        table_name: str,
        uuid_or_list: str | list[str],
        uuid_col: str = "uuid",
        id_col: str = "id",
        with_deleted: bool = False,
    ) -> int | None | list[int | None]:

        if isinstance(uuid_or_list, list):
            return self._resolve_batch(session, table_name, uuid_or_list, uuid_col, id_col, with_deleted)

        if not _is_valid_uuid(uuid_or_list):
            logger.warning(f"Invalid UUID format for table {table_name}: {uuid_or_list}")
            return None

        cache_key = f"{table_name}:{uuid_or_list}"

        cached = cache_manager.get_global("uuid_map", cache_key)
        if cached is not None:
            return int(cached)

        query_parts = [f"SELECT {id_col} FROM {table_name} WHERE {uuid_col} = :uuid"]
        if not with_deleted:
            query_parts.append("AND delete_time IS NULL")

        query = text(" ".join(query_parts))
        result = session.execute(query, {"uuid": uuid_or_list})
        row = result.fetchone()

        if row is None:
            return None

        db_id = row[0]

        cache_manager.set_global("uuid_map", cache_key, db_id)
        return db_id

    def _resolve_batch(
        self,
        session,
        table_name: str,
        uuids: list[str],
        uuid_col: str,
        id_col: str,
        with_deleted: bool,
    ) -> list[int | None]:

        if not uuids:
            return []

        cache_results = {}
        uncached_uuids = []

        for uuid in uuids:
            if not _is_valid_uuid(uuid):
                logger.warning(f"Invalid UUID format for table {table_name}: {uuid}")
                cache_results[uuid] = None
                continue

            cache_key = f"{table_name}:{uuid}"
            cached = cache_manager.get_global("uuid_map", cache_key)
            if cached is not None:
                cache_results[uuid] = int(cached)
            else:
                uncached_uuids.append(uuid)

        if uncached_uuids:
            placeholders = ", ".join([f":uuid_{i}" for i in range(len(uncached_uuids))])
            query_parts = [f"SELECT {id_col}, {uuid_col} FROM {table_name} WHERE {uuid_col} IN ({placeholders})"]
            if not with_deleted:
                query_parts.append("AND delete_time IS NULL")

            query = text(" ".join(query_parts))
            params = {f"uuid_{i}": uuid for i, uuid in enumerate(uncached_uuids)}

            result = session.execute(query, params)
            for row in result:
                db_id = row[0]
                uuid_val = row[1]
                cache_results[uuid_val] = db_id
                cache_key = f"{table_name}:{uuid_val}"
                cache_manager.set_global("uuid_map", cache_key, db_id)

        return [cache_results.get(uuid) for uuid in uuids]


uuid_resolver = UuidResolver()
