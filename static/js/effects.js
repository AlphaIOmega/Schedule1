/**
 * This file contains the mapping of effect names to their corresponding colors.
 * Generated from effects.json
 */

const effectColors = {
    "anti-gravity": "rgb(35, 91, 203)", // Ability
    "athletic": "rgb(117, 200, 253)", // Ability
    "balding": "rgb(199, 146, 50)", // Cosmetic
    "bright-eyed": "rgb(190, 247, 253)", // Ability
    "brighteyed": "rgb(190, 247, 253)", // Ability (alternate spelling)
    "calming": "rgb(254, 208, 155)", // Cosmetic
    "calorie-dense": "rgb(254, 132, 244)", // Cosmetic
    "cyclopean": "rgb(254, 193, 116)", // Cosmetic
    "disorienting": "rgb(254, 117, 81)", // 
    "electrifying": "rgb(85, 200, 253)", // Cosmetic
    "energizing": "rgb(154, 254, 109)", // Ability
    "euphoric": "rgb(254, 234, 116)", // 
    "explosive": "rgb(254, 75, 64)", // Ability
    "focused": "rgb(117, 241, 253)", // 
    "foggy": "rgb(176, 176, 175)", // 
    "gingeritis": "rgb(254, 136, 41)", // Cosmetic
    "glowing": "rgb(133, 228, 89)", // Cosmetic
    "jennerising": "rgb(254, 141, 248)", // Cosmetic
    "laxative": "rgb(118, 60, 37)", // Cosmetic
    "lethal": "rgb(159, 43, 34)", // 
    "long faced": "rgb(254, 217, 97)", // Cosmetic
    "long-faced": "rgb(254, 217, 97)", // Cosmetic (alternate spelling)
    "munchies": "rgb(201, 110, 87)", // 
    "paranoia": "rgb(196, 103, 98)", // 
    "refreshing": "rgb(178, 254, 152)", // 
    "schizophrenia": "rgb(100, 90, 253)", // 
    "sedating": "rgb(107, 95, 216)", // Cosmetic
    "seizure-inducing": "rgb(254, 233, 0)", // Cosmetic
    "shrinking": "rgb(182, 254, 218)", // Cosmetic
    "slippery": "rgb(162, 223, 253)", // Ability
    "smelly": "rgb(125, 188, 49)", // Cosmetic
    "sneaky": "rgb(123, 123, 123)", // 
    "spicy": "rgb(254, 107, 76)", // Cosmetic
    "thought-provoking": "rgb(254, 160, 203)", // Cosmetic
    "thoughtprovoking": "rgb(254, 160, 203)", // Cosmetic (alternate spelling)
    "toxic": "rgb(95, 154, 49)", // Cosmetic
    "tropic thunder": "rgb(254, 159, 71)", // Cosmetic
    "tropic-thunder": "rgb(254, 159, 71)", // Cosmetic (alternate spelling)
    "tropicthunder": "rgb(254, 159, 71)", // Cosmetic (alternate spelling)
    "zombifying": "rgb(113, 171, 93)", // Cosmetic
};

/**
 * Returns the color for a given effect name
 * @param {string} effectName - The name of the effect
 * @returns {string} - The color as an RGB value, or a default color if not found
 */
function getEffectColor(effectName) {
    // Normalize the effect name: convert to lowercase and remove spaces/hyphens
    const normalizedName = effectName.toLowerCase().replace(/[\s-]/g, '');
    
    // Try to find the exact match first
    if (effectColors[effectName.toLowerCase()]) {
        return effectColors[effectName.toLowerCase()];
    }
    
    // Try to find using normalized name
    if (effectColors[normalizedName]) {
        return effectColors[normalizedName];
    }
    
    // Return a default color if not found
    return "#cccccc"; // Light gray
}