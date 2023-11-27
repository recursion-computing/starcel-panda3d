#include "dconfig.h"

#include "kphys/core/panda/animation.h"
#include "kphys/core/panda/animator.h"
#include "kphys/core/panda/armature.h"
#include "kphys/core/panda/bone.h"
#include "kphys/core/panda/bvhq.h"
#include "kphys/core/panda/ccdik.h"
#include "kphys/core/panda/channel.h"
#include "kphys/core/panda/config.h"
#include "kphys/core/panda/controller.h"
#include "kphys/core/panda/converters.h"
#include "kphys/core/panda/effector.h"
#include "kphys/core/panda/frame.h"
#include "kphys/core/panda/hitbox.h"
#include "kphys/core/panda/ik.h"
#include "kphys/core/panda/spring.h"
#include "kphys/core/panda/spring_v1.h"
// #include "kphys/core/panda/spring_v2.h"
#include "kphys/core/panda/types.h"


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

    Animation::init_type();
    AnimatorNode::init_type();
    BVHQ::init_type();
    Channel::init_type();
    Frame::init_type();

    ControllerNode::init_type();
    HitboxNode::init_type();
    SpringConstraint::init_type();
    // Spring2Constraint::init_type();

    ArmatureNode::init_type();
    BoneNode::init_type();
    EffectorNode::init_type();

    return;
}
