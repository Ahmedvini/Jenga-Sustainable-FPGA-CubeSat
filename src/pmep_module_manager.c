/*
 * PMEP module manager demonstration for the SMIS CubeSat electronics platform.
 *
 * This is firmware-style C intended to show the operating logic. Hardware access
 * functions are represented as board support package stubs so the logic can be
 * ported to STM32 HAL, Zephyr, FreeRTOS, or a bare-metal project.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MAX_MODULES 5
#define PMEP_ENUMERATION_TIMEOUT_MS 200

typedef enum {
    MODULE_NONE = 0,
    MODULE_OBC = 1,
    MODULE_POWER = 2,
    MODULE_SENSING = 3,
    MODULE_COMMS = 4,
    MODULE_FPGA_ACCELERATOR = 5
} module_type_t;

typedef enum {
    ORBIT_SUNLIGHT,
    ORBIT_TRANSITION,
    ORBIT_ECLIPSE
} orbit_state_t;

typedef enum {
    POWER_OFF,
    POWER_SLEEP,
    POWER_LOW_RATE,
    POWER_ACTIVE
} power_mode_t;

typedef struct {
    uint8_t slot;
    uint16_t hardware_id;
    module_type_t type;
    uint16_t active_current_ma;
    uint16_t sleep_current_ua;
    uint16_t max_data_rate_hz;
    bool present;
    power_mode_t mode;
} module_descriptor_t;

static module_descriptor_t active_registry[MAX_MODULES];

static bool bsp_detect_line_low(uint8_t slot);
static bool bsp_i2c_read_descriptor(uint8_t slot, module_descriptor_t *descriptor);
static void bsp_power_set(uint8_t slot, power_mode_t mode);
static void bsp_can_register_node(const module_descriptor_t *module);
static uint32_t bsp_millis(void);

static const char *module_name(module_type_t type)
{
    switch (type) {
    case MODULE_OBC:
        return "OBC";
    case MODULE_POWER:
        return "Power";
    case MODULE_SENSING:
        return "Sensing";
    case MODULE_COMMS:
        return "Comms";
    case MODULE_FPGA_ACCELERATOR:
        return "FPGA accelerator";
    default:
        return "None";
    }
}

static bool pmep_enumerate_slot(uint8_t slot)
{
    uint32_t start_ms = bsp_millis();
    module_descriptor_t descriptor;

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.slot = slot;

    while ((bsp_millis() - start_ms) < PMEP_ENUMERATION_TIMEOUT_MS) {
        if (bsp_i2c_read_descriptor(slot, &descriptor)) {
            descriptor.present = true;
            descriptor.mode = POWER_SLEEP;
            active_registry[slot] = descriptor;
            bsp_can_register_node(&active_registry[slot]);
            bsp_power_set(slot, POWER_SLEEP);

            printf(
                "PMEP: slot %u registered %s module, hardware_id=0x%04X\n",
                slot,
                module_name(descriptor.type),
                descriptor.hardware_id
            );
            return true;
        }
    }

    printf("PMEP: slot %u enumeration timed out\n", slot);
    return false;
}

void pmep_scan_slots(void)
{
    for (uint8_t slot = 0; slot < MAX_MODULES; slot++) {
        bool detected = bsp_detect_line_low(slot);

        if (detected && !active_registry[slot].present) {
            pmep_enumerate_slot(slot);
        }

        if (!detected && active_registry[slot].present) {
            printf("PMEP: slot %u removed\n", slot);
            bsp_power_set(slot, POWER_OFF);
            memset(&active_registry[slot], 0, sizeof(active_registry[slot]));
        }
    }
}

void pmep_apply_orbit_power_policy(orbit_state_t state)
{
    for (uint8_t slot = 0; slot < MAX_MODULES; slot++) {
        module_descriptor_t *module = &active_registry[slot];

        if (!module->present) {
            continue;
        }

        switch (state) {
        case ORBIT_SUNLIGHT:
            module->mode = POWER_ACTIVE;
            break;
        case ORBIT_TRANSITION:
            module->mode = (module->type == MODULE_COMMS) ? POWER_SLEEP : POWER_LOW_RATE;
            break;
        case ORBIT_ECLIPSE:
            if (module->type == MODULE_COMMS || module->type == MODULE_FPGA_ACCELERATOR) {
                module->mode = POWER_OFF;
            } else if (module->type == MODULE_SENSING) {
                module->mode = POWER_LOW_RATE;
            } else {
                module->mode = POWER_SLEEP;
            }
            break;
        }

        bsp_power_set(slot, module->mode);
    }
}

/*
 * Board support stubs.
 * Replace these with GPIO, I2C, CAN, timer, and power-switch driver calls.
 */
static bool bsp_detect_line_low(uint8_t slot)
{
    return slot < 4;
}

static bool bsp_i2c_read_descriptor(uint8_t slot, module_descriptor_t *descriptor)
{
    static const module_descriptor_t demo_modules[] = {
        {0, 0x1001, MODULE_OBC, 12, 1, 100, true, POWER_SLEEP},
        {1, 0x2001, MODULE_POWER, 6, 350, 10, true, POWER_SLEEP},
        {2, 0x3001, MODULE_SENSING, 9, 2, 10, true, POWER_SLEEP},
        {3, 0x4001, MODULE_COMMS, 35, 1, 50, true, POWER_SLEEP},
    };

    if (slot >= (sizeof(demo_modules) / sizeof(demo_modules[0]))) {
        return false;
    }

    *descriptor = demo_modules[slot];
    return true;
}

static void bsp_power_set(uint8_t slot, power_mode_t mode)
{
    printf("Power: slot %u -> mode %u\n", slot, mode);
}

static void bsp_can_register_node(const module_descriptor_t *module)
{
    printf("CAN: registered slot %u as %s\n", module->slot, module_name(module->type));
}

static uint32_t bsp_millis(void)
{
    static uint32_t now;
    now += 10;
    return now;
}

#ifdef PMEP_DEMO_MAIN
int main(void)
{
    pmep_scan_slots();
    pmep_apply_orbit_power_policy(ORBIT_SUNLIGHT);
    pmep_apply_orbit_power_policy(ORBIT_ECLIPSE);
    return 0;
}
#endif
