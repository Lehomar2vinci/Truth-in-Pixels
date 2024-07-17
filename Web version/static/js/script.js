document.addEventListener("DOMContentLoaded", () => {
  const deformationCheckbox = document.getElementById("deformation");
  const mirrorCheckbox = document.getElementById("mirror");
  const pointillismCheckbox = document.getElementById("pointillism");
  const facemaskCheckbox = document.getElementById("facemask");
  const colorFilterCheckbox = document.getElementById("colorFilter");
  const blurCheckbox = document.getElementById("blur");
  const vignetteCheckbox = document.getElementById("vignette");
  const sepiaCheckbox = document.getElementById("sepia");
  const cartoonCheckbox = document.getElementById("cartoon");

  const deformationSlider = document.getElementById("deformationIntensity");
  const mirrorSlider = document.getElementById("mirrorIntensity");
  const pointillismSlider = document.getElementById("pointillismSize");
  const facemaskSlider = document.getElementById("facemaskPointSize");
  const colorIntensitySlider = document.getElementById("colorIntensity");
  const blurSlider = document.getElementById("blurIntensity");
  const vignetteSlider = document.getElementById("vignetteIntensity");

  const applyEffectsButton = document.getElementById("applyEffects");

  applyEffectsButton.addEventListener("click", () => {
    const selectedEffects = [];
    if (deformationCheckbox.checked) selectedEffects.push("Deformation");
    if (mirrorCheckbox.checked) selectedEffects.push("Mirror");
    if (pointillismCheckbox.checked) selectedEffects.push("Pointillism");
    if (facemaskCheckbox.checked) selectedEffects.push("Face Mask");
    if (colorFilterCheckbox.checked) selectedEffects.push("Color Filter");
    if (blurCheckbox.checked) selectedEffects.push("Blur");
    if (vignetteCheckbox.checked) selectedEffects.push("Vignette");
    if (sepiaCheckbox.checked) selectedEffects.push("Sepia");
    if (cartoonCheckbox.checked) selectedEffects.push("Cartoon");

    const effects = {
      deformation_intensity: parseInt(deformationSlider.value),
      pointillism_size: parseInt(pointillismSlider.value),
      facemask_point_size: parseInt(facemaskSlider.value),
      mirror_intensity: parseInt(mirrorSlider.value),
      color_intensity: parseInt(colorIntensitySlider.value),
      blur_intensity: parseInt(blurSlider.value),
      vignette_intensity: parseInt(vignetteSlider.value),
      selected_effects: selectedEffects,
    };

    fetch("/update_effects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(effects),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          console.log("Effects updated successfully");
        } else {
          console.log("Failed to update effects");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
});
