import { HttpResponse } from 'msw'

export function ok<T>(data: T) {
  return HttpResponse.json({ status: 1, data, msg: 'success' })
}

export function fail(msg: string, httpStatus = 400) {
  return HttpResponse.json(
    { status: 0, data: null, error: msg, msg },
    { status: httpStatus },
  )
}
