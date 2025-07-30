# Regex characters
RX_CHAR = r'([A-Z][A-Z0-9_]*)'
# Regex for Sets, functions and relations (without parentheses)
RX_SET  = RX_CHAR
RX_ARG  = fr'\[{RX_CHAR}\]'
RX_FUN  = fr'{RX_CHAR}{RX_ARG}'
RX_REL  = fr'\*{RX_FUN}'
# Regex for calls to sets, functions and relations (with parentheses)
RX_SET_ = fr'\({RX_SET}\)'
RX_FUN_ = fr'\({RX_FUN}\)'
RX_REL_ = fr'\({RX_REL}\)'

# Print (for debugging)
# for name, value in list(globals().items()):
#     if name.isupper():
#         print(f"{name} = {value}")

# For development
from re import search as re_search
from re import findall as re_findall
txt = '(FUN1[SET1])...(FUNN[SETN])'
# txt = 'SUPER DUMB'
m = re_findall( RX_FUN_, txt)
print(f'txt = {txt} -> match_groups = {m}')
