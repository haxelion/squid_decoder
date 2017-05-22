import sys
import papyrus_pb2
import cairocffi
import math

DPI = 72 # defined by cairocffi
def cm_to_point(cm):
    return cm / 2.54 * DPI

def u32_to_4f(u):
    return [((u>>24) & 0xFF) / 255.0, ((u>>16) & 0xFF) / 255.0, ((u>>8) & 0xFF) / 255.0, (u & 0xFF) / 255.0]

if __name__ == '__main__':
    page = papyrus_pb2.Page()
    # Open and parse papyrus page using protobuf
    page.ParseFromString(open(sys.argv[1], 'rb').read())
    # Create a new svg surface for drawing

    if page.background.width == 0 and page.background.height == 0:
        print("Infinite page!")
        page.background.width = 50
        page.background.height = 150

    surface = cairocffi.SVGSurface(open(sys.argv[2], 'w'), cm_to_point(page.background.width), cm_to_point(page.background.height))
    context = cairocffi.Context(surface)

    # Paint the page white
    context.set_source_rgb(1, 1, 1)
    context.paint()

    for item in page.layer.item:
        #print "Item"
        if item.type == papyrus_pb2.Item.Type.Value('Stroke'):
            context.save()
            # Translate to reference_point (stroke origin)
            context.translate(cm_to_point(item.stroke.reference_point.x), cm_to_point(item.stroke.reference_point.y))
            # Set source color
            argb = u32_to_4f(item.stroke.color)
            context.set_source_rgba(argb[1], argb[2], argb[3], argb[0])
            # Set line width
            width = cm_to_point(item.stroke.weight)
            # Other parameter
            context.set_line_join(cairocffi.LINE_JOIN_ROUND)
            context.set_line_cap(cairocffi.LINE_CAP_ROUND)
            context.move_to(0,0)

            for point in item.stroke.point:
                context.line_to(cm_to_point(point.x), cm_to_point(point.y))
                if point.HasField('pressure'):
                    context.set_line_width(width * point.pressure)
                else:
                    context.set_line_width(width)
                context.stroke()
                context.move_to(cm_to_point(point.x), cm_to_point(point.y))
            context.restore()
        elif item.type == papyrus_pb2.Item.Type.Value('Shape') and item.shape.ellipse is not None:
            context.save()
            context.translate(cm_to_point(item.shape.ellipse.center_x), cm_to_point(item.shape.ellipse.center_y))
            context.move_to(0,0);

            argb = u32_to_4f(item.shape.ellipse.color)
            context.set_source_rgba(argb[1], argb[2], argb[3], argb[0])
            context.scale(cm_to_point(item.shape.ellipse.radius_x), cm_to_point(item.shape.ellipse.radius_y))
            context.arc(0, 0, 1, 0, 2 * math.pi)
            context.restore()
        else:
            print(item.shape)
            print(item.shape.ellipse)
            print("Item of type {} not supported".format(papyrus_pb2.Item.Type.Name(item.type)))
    surface.flush()
    surface.finish()
