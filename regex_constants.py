# Regex characters
RX_CHAR = r'([A-Z][A-Z0-9_]*)'
# Regex for Sets, functions and relations (without parentheses)
RX_SET  = RX_CHAR
RX_FUN  = fr'{RX_CHAR}\[{RX_CHAR}\]'
RX_REL  = fr'\*{RX_FUN}'
# Regex for calls to sets, functions and relations (with parentheses)
RX_SET_ = fr'\({RX_SET}\)'
RX_FUN_ = fr'\({RX_FUN}\)'
RX_REL_ = fr'\({RX_REL}\)'

# Print (for debugging)
for name, value in list(globals().items()):
    if name.isupper():
        print(f"{name} = {value}")
