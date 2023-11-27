#include "dconfig.h"

#include "krender/core/config.h"
#include "krender/core/lighting_pipeline.h"
#include "krender/core/progress_bar.h"
#include "krender/core/render_pass.h"
#include "krender/core/render_pipeline.h"


Configure(config_core);
NotifyCategoryDef(core, "");

ConfigureFn(config_core) {
    init_libcore();
}

void init_libcore() {
    static bool initialized = false;
    if (initialized)
        return;
    initialized = true;

    RenderPipeline::init_type();
    LightingPipeline::init_type();
    ProgressBar::init_type();

    return;
}
