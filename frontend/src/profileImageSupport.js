import placeholderImage from './assets/placeholder600x400.png'
import patientDefaultFemale from './assets/patient-default-female.png'
import patientDefaultMale from './assets/patient-default-male.png'

export function resolveProfileImageSrc({ src, gender }) {
  if (src) {
    return src
  }

  if (gender === 'female') {
    return patientDefaultFemale
  }

  if (gender === 'male') {
    return patientDefaultMale
  }

  return placeholderImage
}

export function getProfileImageFallbackSrc() {
  return placeholderImage
}
