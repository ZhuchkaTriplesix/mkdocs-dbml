from typing import Dict, Set


class GraphLayoutEngine:
    def __init__(self, tables, refs):
        self.tables = {table.name: table for table in tables}
        self.refs = refs
        self.graph = self._build_graph()

    def _build_graph(self) -> Dict[str, Set[str]]:
        graph = {name: set() for name in self.tables.keys()}

        for ref in self.refs:
            if ref.col1 and ref.col2:
                col1 = ref.col1[0]
                col2 = ref.col2[0]
                if col1 and col2:
                    table1 = col1.table.name
                    table2 = col2.table.name
                    if table1 in graph and table2 in graph:
                        graph[table1].add(table2)
                        graph[table2].add(table1)

        return graph

    def calculate_positions(
        self, col_width=300, h_spacing=200, v_spacing=120, padding=60
    ):
        positions = {}
        dimensions = {}

        table_list = list(self.tables.keys())
        visited = set()
        layers = []

        if not table_list:
            return positions, dimensions

        start_table = self._find_central_table()
        visited.add(start_table)
        current_layer = [start_table]

        while current_layer:
            layers.append(current_layer)
            next_layer = []

            for table in current_layer:
                for neighbor in self.graph.get(table, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_layer.append(neighbor)

            current_layer = next_layer

        for table in table_list:
            if table not in visited:
                layers.append([table])

        for layer_idx, layer in enumerate(layers):
            start_x = padding

            for col_idx, table_name in enumerate(layer):
                table = self.tables[table_name]

                x = start_x + col_idx * (col_width + h_spacing)
                y = padding + layer_idx * (300 + v_spacing)

                field_count = len(table.columns)
                height = 48 + (field_count * 36) + 12

                positions[table_name] = (x, y)
                dimensions[table_name] = (col_width, height)

        return positions, dimensions

    def _find_central_table(self) -> str:
        if not self.graph:
            return list(self.tables.keys())[0]

        max_connections = 0
        central_table = list(self.tables.keys())[0]

        for table, connections in self.graph.items():
            if len(connections) > max_connections:
                max_connections = len(connections)
                central_table = table

        return central_table
