
from pymtl3.passes.backends.verilog import TranslationConfigs

# Only using PyMTL version
from .BlockingCachePRTL import BlockingCachePRTL

class BlockingCacheRTL( BlockingCachePRTL ):
  def construct( s, num_banks=0 ):
    super().construct( num_banks )

    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = f'cache_BlockingCacheRTL_{num_banks}bank',
    )
