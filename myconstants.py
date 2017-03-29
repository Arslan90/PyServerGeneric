

# ****************************************
# VERSION
# ****************************************
VERSION = 1

# ****************************************
# COMMANDS
# ****************************************
# Basics: 0x0X
NBR_ARGUMENTS = 0x01
# command, query, response
QUERY = 0x02
RESPONSE = 0x03

# ****************************************
# COMMANDS VALUES
# ****************************************
# Commands values: 0x1X
CMD_NP_ALL = 0x11
RESPONSE_NP_ALL = 0x12

CMD_EDGE_BEST_TRAVEL_TIME = 0x13
RESPONSE_EDGE_BEST_TRAVEL_TIME = 0x14

# ****************************************
# NP RELATED
# ****************************************
# DATA Related to Nearest point node (NP): 0x2X
EDGE_TO_NP = 0x26
NODE_NP = 0x27
EDGE_FROM_NP = 0x28

# ****************************************
# VPA RELATED
# ****************************************
# DATA Related to VPA: 0x3X
VPA_SECTOR_ID = 0x31
VPA_MAPPING_TYPE = 0x32
VPA_MAPPING_NBR = 0x32

EDGE_TO_VPA_MAPPING = 0x36
NODE_VPA_MAPPING = 0x37
EDGE_FROM_VPA_MAPPING = 0x38

# ****************************************
# ROUTE RELATED
# ****************************************
# ROUTE RELATED : 0x5X
ROUTE_CURRENT = 0x51 # as a list of edges, edged route
ROUTE_LENGTH_CURRENT = 0x52
ROUTE_NP_VPA = 0x53
ROUTE_LENGTH_NP_VPA = 0x54

# ****************************************
# EDGE RELATED
# ****************************************
# EDGE RELATED : 0x6X
EDGE_ID = 0x61
EDGE_BEST_TRAVEL_TIME = 0x62 # as a list of edges, edged route


# ****************************************
# SPECIAL COMMAND RELATED
# ****************************************
# SPECIAL COMMAND = 0x7X
HOTSPOT_MODE = 0x71

# ****************************************
# COMMAND Arguments type
# ****************************************
# COMMAND Arguments type: 0x8x
BOOL = 0x81
INT = 0x82
FLOAT = 0x83
STRING = 0x84
LIST_STRING = 0x85
MAPPING_VPA = 0x86
T_NODE = "NODE"
T_EDGE = "EDGE"
T_NONE = "NONE"

# ****************************************
# DICO FOR Arguments type
# ****************************************
DICO_ARG_TYPE = {NBR_ARGUMENTS : INT,
                 EDGE_TO_NP : STRING,
                 NODE_NP : STRING,
                 EDGE_FROM_NP  : STRING,
                 VPA_SECTOR_ID  : INT,
                 VPA_MAPPING_TYPE  : MAPPING_VPA,
                 VPA_MAPPING_NBR  : INT,
                 EDGE_TO_VPA_MAPPING  : STRING,
                 NODE_VPA_MAPPING  : STRING,
                 EDGE_FROM_VPA_MAPPING  : STRING,
                 ROUTE_CURRENT  : LIST_STRING,
                 ROUTE_LENGTH_CURRENT  : FLOAT,
                 ROUTE_NP_VPA  : LIST_STRING,
                 ROUTE_LENGTH_NP_VPA  : FLOAT,
                 EDGE_ID : STRING,
                 EDGE_BEST_TRAVEL_TIME : FLOAT,
                 HOTSPOT_MODE : STRING}

KNOWN_QUERIES = [CMD_NP_ALL, CMD_EDGE_BEST_TRAVEL_TIME]
KNOWN_RESPONSES = [RESPONSE_NP_ALL, RESPONSE_EDGE_BEST_TRAVEL_TIME]

FORMAT_QUERIES = {CMD_NP_ALL: [VPA_SECTOR_ID, DICO_ARG_TYPE[VPA_SECTOR_ID], ROUTE_CURRENT, DICO_ARG_TYPE[ROUTE_CURRENT], HOTSPOT_MODE, DICO_ARG_TYPE[HOTSPOT_MODE]],
                  CMD_EDGE_BEST_TRAVEL_TIME: [EDGE_ID, DICO_ARG_TYPE[EDGE_ID]]}
FORMAT_RESPONSES = {RESPONSE_NP_ALL: [],
                    RESPONSE_EDGE_BEST_TRAVEL_TIME: []}



