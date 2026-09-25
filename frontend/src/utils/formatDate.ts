
export function formatDate (dateSting : string | undefined): string {
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }
  if (!dateSting){
    return " "
  }
  return new Date(dateSting).toLocaleDateString("en-US",{year:'numeric',month:"2-digit",day:"2-digit"})
}
