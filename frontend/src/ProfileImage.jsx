import { getProfileImageFallbackSrc, resolveProfileImageSrc } from './profileImageSupport'

export function ProfileImage({ alt = '', className = '', src, gender = null }) {
  const handleError = (event) => {
    if (!event.currentTarget.dataset.fallbackApplied) {
      event.currentTarget.dataset.fallbackApplied = 'true'
      event.currentTarget.src = getProfileImageFallbackSrc()
    }
  }

  return (
    <img
      alt={alt}
      className={className}
      src={resolveProfileImageSrc({ src, gender })}
      onError={handleError}
      loading="lazy"
    />
  )
}
